import string
import random
from utils.operations import semantic_signal, commit_signal
from user_registration.apps import *
from user_registration.models import *
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
    return [effect] #[complete_effect(effect, message.logger_msg, COMMIT, opcode="PL")]


# Taken from CreateDataMixin in rapidsms.tests.harness.base
def random_string(self, length=255, extra_chars=''):
    """
    Generate a random string of characters.

    :param length: Length of generated string.
    :param extra_chars: Additional characters to include in generated string.
    """

    chars = string.letters + extra_chars
    return ''.join([random.choice(chars) for i in range(length)])

@receiver(commit_signal, sender=UserRegistration)
def user_registration_commit(sender, message, **kwargs):
    # Check if a Connection for this new user already exists
    connection = get_connection(kwargs['phone_number'])
    if connection is not None:
        effect = error(
                _("Error: Contact already exists"), {},
                _("Contact with phone number %(phone_number)s already exists"), { 'phone_number' : kwargs['phone_number'] }
                )

    else:
        backend_data = {'name' : random_string(12)}
        contact_data = {}
        if 'contact_name' in kwargs.keys():
            contact_data['name'] = kwargs['contact_name']

        connection_data = {'identity' : kwargs['phone_number'], 
                           'backend' : Backend.objects.create(**backend_data),
                           'contact' : Contact.objects.create(**contact_data)}
        Connection.objects.create(**connection_data)

        #TODO: Add name info?????
        effect = info(
                _("Registered New User"), {},
                _("Phone number: %(phone_number)s"), { 'phone_number' : kwargs['phone_number'] }
                )
    return [effect] #[complete_effect(effect, message.logger_msg, COMMIT, opcode="RG")]

