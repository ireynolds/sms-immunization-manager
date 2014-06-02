from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.translation import check_for_language
from django.utils.http import is_safe_url
from django.contrib import messages
from django.utils.translation import ugettext as _
from user_registration.models import *
from moderation.models import *
from rapidsms.contrib.messagelog.models import Message
from rapidsms.router import receive, lookup_connections
from forms import *

@login_required
def home(request):
    """
    Redirects to a user's affiliated facility, or the list of root nodes if no affiliation exists.
    """
    default_url = reverse(root_nodes)

    if request.user.moderator_profile != None:
        home_url = request.user.moderator_profile.get_home_url()
        if home_url != None:
            return HttpResponseRedirect(home_url)

    return HttpResponseRedirect(default_url)

@login_required
def root_nodes(request):
    """
    Lists the root hierarchy nodes
    """
    # TODO: collect

    nodes = HierarchyNode.objects.filter(parent=None)
    return render_to_response('root_nodes.html', {'nodes': nodes},
        context_instance=RequestContext(request))

@login_required
def node(request, node_id):
    """
    Displays a single hierarchy node
    """
    node = get_object_or_404(HierarchyNode, pk=node_id)
    return render_to_response("node.html", {"node": node},
        context_instance=RequestContext(request))

@login_required
def facility(request, facility_id):
    """
    Displays a summary of a facility
    """
    facility = get_object_or_404(Facility, pk=facility_id)
    return render_to_response("facility.html", {'facility': facility},
        context_instance=RequestContext(request))

@login_required
def contact(request, contact_id):
    """
    Displays a summary of a contact
    """
    class MessageWrapper(object):
        """
        A class which wraps a message and provides additional behavior needed by templates.
        """
        def __init__(self, message):
            self.message = message
            self.effects = message.messageeffect_set.all()
            self.wrapped_effects = map(EffectWrapper, self.effects)
            self.needs_action = self.effects.filter(priority__in=MODERATOR_PRIORITIES, 
                moderator_dismissed=False).exists()
            self.dismissed = (not self.needs_action 
                and self.effects.filter(priority__in=MODERATOR_PRIORITIES).exists())
            self.created_by_moderator = message.connection.backend.name == settings.MODERATOR_BACKEND

    class EffectWrapper(object):
        """
        A class which wraps a message effect and provides additional behavior needed by templates.
        """
        ROW_CLASSES = {
            DEBUG: '',
            INFO: '',
            WARN: '',
            ERROR: 'danger',
            URGENT: '',
        }
        LABEL_CLASSES = {
            DEBUG: 'info',
            INFO: 'success',
            WARN: 'warning',
            ERROR: 'danger',
            URGENT: 'warning',
        }
        def __init__(self, effect):
            self.effect = effect
            self.row_class = self.ROW_CLASSES[effect.priority]
            self.label_class = self.LABEL_CLASSES[effect.priority]
            self.dismissable = (effect.priority in MODERATOR_PRIORITIES 
                and not effect.moderator_dismissed)
            self.undismissable = (effect.priority in MODERATOR_PRIORITIES 
                and effect.moderator_dismissed)

    contact = get_object_or_404(Contact, pk=contact_id)

    wrapped_messages = map(MessageWrapper, contact.message_set.order_by('-date'))
    #contact_revisions = reversion.get_for_object(self)


    return render_to_response("contact.html", 
        {   'contact': contact,
            'wrapped_messages': wrapped_messages,
        },
        context_instance=RequestContext(request))

@login_required
def contact_edit(request, contact_id):
    """
    Edits the given contact
    """
    contact = get_object_or_404(Contact, pk=contact_id)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        profile_form = ContactProfileForm(request.POST, instance=contact.contactprofile)

        if form.is_valid() and profile_form.is_valid():
            contact = form.save()
            profile_form.save()

            messages.success(request, _("The contact %(name)s was successfully updated") % 
                {'name': unicode(contact)})
            return HttpResponseRedirect(reverse("moderation.views.contact", args=(contact.pk,)))
    else:
        form = ContactForm(instance=contact)
        profile_form = ContactProfileForm(instance=contact.contactprofile)

    return render_to_response("contact_edit.html", 
        {   'contact': contact, 
            'form': form, 
            'profile_form': profile_form,
        },
        context_instance=RequestContext(request))

@login_required
def contact_create(request):
    """
    Creates a new contact. May be passed optional GET parameters 'facility' and 'phone_number' that
    pre-populate the creation form.
    """

    if request.method == "POST":
        form = ContactForm(request.POST)
        profile_form = ContactProfileForm(request.POST)

        if form.is_valid() and profile_form.is_valid():
            contact = form.save()

            # Populate the required 'contact' field before saving
            profile = profile_form.save(commit=False)
            profile.contact = contact
            profile.save()

            messages.success(request, _("The contact %(name)s was successfully created") % 
                {'name': unicode(contact)})
            return HttpResponseRedirect(reverse("moderation.views.contact", args=(contact.pk,)))
    else:
        form_initial = {'phone_number': request.GET.get('phone_number', '')}
        form = ContactForm(initial=form_initial)

        profile_initial = {}
        if "facility" in request.GET:
            facility = get_object_or_404(Facility, pk=request.GET['facility'])
            profile_initial['facility'] = facility.pk
        profile_form = ContactProfileForm(initial=profile_initial)

    return render_to_response("contact_create.html", 
        {   'form': form, 
            'profile_form': profile_form,
        },
        context_instance=RequestContext(request))

@login_required
def message_resend(request, message_id):
    """
    Re-sends the given message
    """
    message = get_object_or_404(Message, pk=message_id)
    contact = message.contact

    if request.method == 'POST':
        form = ResendForm(request.POST)

        if form.is_valid():
            text = form.cleaned_data['text']
            number = contact.contactprofile.get_phone_number()

            connection = lookup_connections(settings.MODERATOR_BACKEND, [number])[0]
            receive(text, connection)

            messages.success(request, _("The message %(text)s was successfully resent") % 
                    {'text': unicode(text)})

            return HttpResponseRedirect(reverse("moderation.views.contact", args=(contact.pk,)))
    else:
        form = ResendForm(initial={'text': message.text})

    return render_to_response("message_resend.html", 
        {   'contact': contact,
            'message': message,
            'form': form, 
        },
        context_instance=RequestContext(request))


def get_redirect_url(request):
    """
    Returns a redirect URL based on a 'next' POST variable, a 'next' GET variable, or the
    request's referer (in that order). If none are set, returns "/".
    """
    next = request.POST.get('next', request.GET.get('next'))
    if not is_safe_url(url=next, host=request.get_host()):
        next = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=next, host=request.get_host()):
            next = '/'
    return next

@login_required
def effect_dismiss(request, effect_id, dismiss_value):
    """
    Sets the dismissal state of the given effect to dismiss_value. Redirects to the contact view
    of the sender of the message containing the given effect.
    """
    if request.method == 'POST':
        effect = get_object_or_404(MessageEffect, pk=effect_id)
        effect.moderator_dismissed = dismiss_value
        effect.save()
        return HttpResponseRedirect(get_redirect_url(request))
    else:
        return HttpResponseNotAllowed(['POST']) 

@login_required
def message_dismiss(request, message_id):
    """
    Dismisses all effects requiring moderator action in the given message.
    """
    if request.method == 'POST':
        message = get_object_or_404(Message, pk=message_id)
        effects = message.messageeffect_set.filter(priority__in=MODERATOR_PRIORITIES)
        effects.update(moderator_dismissed=True)
        return HttpResponseRedirect(get_redirect_url(request))
    else:
        return HttpResponseNotAllowed(['POST']) 

@login_required
def contact_dismiss(request, contact_id):
    """
    Dismisses all effects requiring moderator action in the given contact
    """
    if request.method == 'POST':
        contact = get_object_or_404(Contact, pk=contact_id)
        effects = MessageEffect.objects.filter(message__contact=contact, 
            priority__in=MODERATOR_PRIORITIES)
        effects.update(moderator_dismissed=True)
        return HttpResponseRedirect(get_redirect_url(request))
    else:
        return HttpResponseNotAllowed(['POST'])

def set_language(request):
    """
    Sets the user's session language. Based on the view django.views.i18n in Django 1.7, with slight
    modifications to make the view exclusively use sessions for storing a prefered language.
    """
    response = HttpResponseRedirect(get_redirect_url(request))

    if request.method == 'POST':
        lang_code = request.POST.get('language', None)
        if lang_code and check_for_language(lang_code):
            request.session[settings.LANGUAGE_SESSION_KEY] = lang_code

    return response

@login_required
def set_default_language(request):
    """
    Sets the user's default language.
    """
    response = HttpResponseRedirect(get_redirect_url(request))

    if request.method == 'POST':
        lang_code = request.POST.get('language', None)
        if lang_code and check_for_language(lang_code):
            request.user.moderator_profile.language = lang_code
            request.user.moderator_profile.save()
            messages.success(request, _("Your default language has been updated."))

    return response

@login_required
def set_affiliation(request):
    """
    Sets the user's node and/or facility affiliation. May only be accessed via POST, and returns
    400 if the request is malformed.
    """
    if request.method == 'POST':
        form = ModeratorAffiliationForm(request.POST, instance=request.user.moderator_profile)
        if form.is_valid():
            form.save()
            messages.success(request, _("Your default page has been updated."))
            return HttpResponseRedirect(reverse(home))
        else:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed(['POST'])