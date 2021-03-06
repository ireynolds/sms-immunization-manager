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
    if connection is not None and connection.contact is not None:
        effect = error(
                _("Error: Contact already exists"), {},
                _("Contact with phone number %(phone_number)s already exists"), { 'phone_number' : kwargs['phone_number'] }
                )

    else:
        # create a new rapidSMS Contact
        contact_data = {}
        if 'contact_name' in kwargs:
            contact_data['name'] = kwargs['contact_name']

        contact = Contact.objects.create(**contact_data)

        if connection is None:
            # get or create a new Backend
            backend = get_backend(settings.PHONE_BACKEND)
            if backend is None:
                backend = Backend.objects.create(name=settings.PHONE_BACKEND)

            # make a Connection for this user
            connection_data = {'identity' : kwargs['phone_number'], 
                               'backend' : backend,
                               'contact' : contact}
            Connection.objects.create(**connection_data)
        else:
            connection.contact = contact
            connection.save()

        # update this user's facility. If a facility code was provided,
        # set new user's facility to the requested facility. Otherwise,
        # find the facility of the Admin registering this new user,
        # and use that facility
        contact_profile = ContactProfile.objects.get(contact=contact)
        if 'facility' in message.fields:
            contact_profile.facility = message.fields['facility']
        else:
            contact_profile.facility = message.connections[0].contact.contactprofile.facility
        contact_profile.save()
        effect = info(
                _("Registered New User"), {},
                _("Phone number: %(phone_number)s"), { 'phone_number' : kwargs['phone_number'] }
                )
    return [effect]

