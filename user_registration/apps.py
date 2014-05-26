import django.dispatch
from django.conf import settings
from utils.operations import OperationBase
from operation_parser import gobbler
from moderation.models import *
from django.utils.translation import ugettext_noop as _

# TODO: extract out _errors into Base class??

class PreferredLanguage(OperationBase):
    """Implements the SMS API for setting a user's preferred language."""

    # TODO: Change help string to reflect settings??
    helptext = "For example, %(opcode)s 1. Sets the preferred language to English"

    # TODO: this is basically copied from help.apps -- extract to somewhere?
    def _ok(self, opcode, args):
        """
        Return a MessageEffect that indicates success.
        """
        return ok_parse(opcode, "Parsed: requested language is %(preferred_lang)s", args)

    def _error_extra_chars(self, opcode, arg_string):
        """
        Return a MessageEffect that indicates a failure as a result of
        the arguments having extra chars after the preferred language code.
        """
        return error_parse(opcode, arg_string, reason="Text after preferred language code not allowed.")

    def _error_unrecognized_chars(self, opcode, arg_string):
        """
        Return a MessageEffect that indicates a failure as a result of
        the arguments containing unrecognized characters in the argument string
        instead of a recognized language code.
        """
        return error_parse(opcode, arg_string, reason="Should start with a recognized language code.")

    def _error_no_lang_code(self, opcode, arg_string):
        """
        Return a MessageEffect that indicates a failure as a result of
        the arguments being empty.
        """
        return error_parse(opcode, arg_string, reason="Must request a specific language code.")

    def parse_arguments(self, opcode, arg_string, message):
        args = {}

        lang_code, remaining = gobbler.gobble(settings.PREFERRED_LANGUAGE_CODE, arg_string) 
        
        if lang_code:
            if remaining:
                effect, args = self._error_extra_chars(opcode, arg_string), None
            else:
                lang_code = int(lang_code)
                args['preferred_lang_code'] = lang_code
                args['preferred_lang'] = settings.PREFERRED_LANGUAGES[lang_code]
                effect = self._ok(opcode, args)
        else:
            if remaining:
                effect, args = self._error_unrecognized_chars(opcode, arg_string), None
            else:
                effect, args = self._error_no_lang_code(opcode, arg_string), None

        return ([effect], args)

# TODO: Fix the regex
PHONE_NUMBER = "\d{8}|\d{4}-\d{4}|\+\d{13}"
class UserRegistration(OperationBase):
    """Implements the SMS API for registering a new user."""
    # TODO: complete this
    helptext = "For example....."

    # TODO: should this be %(phone_number) instead?
    def _ok_phone(self, opcode, args):
        """
        Return a MessageEffect that indicates success.
        """
        return ok_parse(opcode, "Parsed: phone number to register is %(phone_number)s", args)

    def _ok_phone_and_name(self, opcode, args):
        """
        Return a MessageEffect that indicates success.
        """
        return ok_parse(opcode, "Parsed: phone number to register for %(contact_name) is %(phone_number)s", args)

    #TODO: Make error message more helpful??? i.e. what is proper format?

    def _error_invalid_phone_number(self, opcode, arg_string):
        """
        Return a MessageEffect that indicates a failure as a result of
        the arguments containing unrecognized characters in the argument string
        instead of a phone number.
        """
        return error_parse(opcode, arg_string, reason="Should start with a properly formatted phone number.")

    def _error_no_phone_number(self, opcode, arg_string):
        """
        Return a MessageEffect that indicates a failure as a result of
        the arguments being empty.
        """
        return error_parse(opcode, arg_string, reason="Must include a phone number to register for this new user.")

    def parse_arguments(self, opcode, arg_string, message):
        args = {} 
        phone_number, remaining = gobbler.gobble(PHONE_NUMBER, arg_string)

        if phone_number is None:
            if remaining:
                effect, args = self._error_invalid_phone_number(opcode, arg_string), None
            else:
                effect, args = self._error_no_phone_number(opcode, arg_string), None
        else:
            args['phone_number'] = phone_number
            if remaining:
                # Treats all text after phone number as user name
                args['contact_name'] = contact_name
                effect = self._ok_phone_and_name(opcode, args)
            else:
                effect = self._ok_phone(opcode, args)


#        contact_name, remaining = gobbler.gobble(NAME, remaining)
#
#        if contact_name:
#            if remaining:
#                effect = _error_extra_chars(opcode, arg_string)
#            else:
#                args['phone_number'] = phone_number
#                args['contact_name'] = contact_name
#                effect = _ok_phone_and_name(opcode, args)
#        else:
#            if remaining:
#                #TODO: error unrecognized characters
#                pass
#            else:
#                args['phone_number'] = phone_number
#                effect = _ok_phone(opcode, args)
#
        return [effect], args
