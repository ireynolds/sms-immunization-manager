from models import *
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
from forms import ModeratorAffiliationForm

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

def root_moderation_contacts():
    """
    Returns a QuerySet of Contacts with no Facility affiliation that have undismissed MessageEffects
    that require moderator action.
    """
    pass

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
    return render_to_response("contact.html", context_instance=RequestContext(request))

@login_required
def contact_edit(request, contact_id):
    """
    Edits a contact
    """
    return render_to_response("contact_edit.html", context_instance=RequestContext(request))

def set_language(request):
    """
    Sets the user's session language. Based on the view django.views.i18n in Django 1.7, with slight
    modifications to make the view exclusively use sessions for storing a prefered language.
    """
    next = request.POST.get('next', request.GET.get('next'))
    if not is_safe_url(url=next, host=request.get_host()):
        next = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=next, host=request.get_host()):
            next = '/'
    response = HttpResponseRedirect(next)

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
    next = request.POST.get('next', request.GET.get('next'))
    if not is_safe_url(url=next, host=request.get_host()):
        next = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=next, host=request.get_host()):
            next = '/'
    response = HttpResponseRedirect(next)

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
