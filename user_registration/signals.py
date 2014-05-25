from utils.operations import semantic_signal, commit_signal
from user_registration.apps import *
from user_registration.models import *
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_noop as _

@receiver(commit_signal, sender=PreferredLanguage)
def preferred_language_commit(message, **kwargs):
    contact = message.connections[0].contact
    preferred_lang = kwargs['preferred_lang']
    contact.language = preferred_lang
    contact.save()

    result_fmtstr = _("Changed language preference to %(language)s")
    result_context = {"language" : preferred_lang}
    effect = info(_("Changed Language Preferences"), {}, result_fmtstr, result_context)
    return [complete_effect(effect, message.logger_msg, COMMIT, opcode="PL")]
