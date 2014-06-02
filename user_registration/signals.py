from utils.operations import semantic_signal, commit_signal
from user_registration.apps import *
from user_registration.models import *
from django.conf import settings
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_noop as _
from rapidsms.models import Backend, Contact, Connection

@receiver(commit_signal, sender=PreferredLanguage)
def preferred_language_commit(message, **kwargs):
    contact = message.connections[0].contact
    preferred_lang = kwargs['preferred_lang']
    contact.language = preferred_lang
    contact.save()

    result_fmtstr = _("Changed language preference to %(language)s")
    result_context = {"language" : preferred_lang}
    effect = info(_("Changed Language Preferences"), {}, result_fmtstr, result_context)
    return [effect]

@receiver(commit_signal, sender=UserRegistration)
def user_registration_commit(message, **kwargs):
    # Check if a Connection for this new user already exists
    connection = get_connection(kwargs['phone_number'])
    if connection is not None:
        effect = error(
                _("Error: Contact already exists"), {},
                _("Contact with phone number %(phone_number)s already exists"), { 'phone_number' : kwargs['phone_number'] }
                )

    else:
        #TODO: Add facility
        contact_data = {}
        if 'contact_name' in kwargs.keys():
            contact_data['name'] = kwargs['contact_name']

#        if message.fields['facility'] is not None:
#            contact_data['facility'] = message.fields['facility']
#        else:
#            # Find the facility of the Admin registering this new user, and use that
#            contact_data['facility'] = message.connections[0].contact.contactprofile.facility

        
        backend = get_backend(settings.PHONE_BACKEND)
        if backend is None:
            backend = Backend.objects.create(name=settings.PHONE_BACKEND)

        connection_data = {'identity' : kwargs['phone_number'], 
                           'backend' : backend,
                           'contact' : Contact.objects.create(**contact_data)}
        Connection.objects.create(**connection_data)

        effect = info(
                _("Registered New User"), {},
                _("Phone number: %(phone_number)s"), { 'phone_number' : kwargs['phone_number'] }
                )
    return [effect]

