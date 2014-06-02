import django.dispatch
from django.conf import settings
from utils.operations import OperationBase
from operation_parser import gobbler
from moderation.models import *
from django.utils.translation import ugettext_noop as _

class PreferredLanguage(OperationBase):
    """Implements the SMS API for setting a user's preferred language."""

    # TODO: Change help string to reflect settings??
    helptext = "For example, %(opcode)s 1. Sets the preferred language to English"

    def _ok(self, opcode, args):
        """
        Return a MessageEffect that indicates success.
        """
        return info(
            _("Parsed %(op_code)s Arguments"), { 'op_code' : opcode },
            _("Parsed: requested language is %(preferred_lang)s"), args
        )

    def _error_extra_chars(self, opcode, arg_string):
        """
        Return a MessageEffect that indicates a failure as a result of
        the arguments having extra chars after the preferred language code.
        """
        return error(
                _("Error Parsing %(op_code)s Arguments"), { 'op_code' : opcode },
                _("Text after preferred language code is not allowed."), {}
        )

    def _error_unrecognized_chars(self, opcode, arg_string):
        """
        Return a MessageEffect that indicates a failure as a result of
        the arguments containing unrecognized characters in the argument string
        instead of a recognized language code.
        """
        return error(
                _("Error Parsing %(op_code)s Arguments"), { 'op_code' : opcode },
                _("Should start with a recognized language code."), {}
        )

    def _error_no_lang_code(self, opcode, arg_string):
        """
        Return a MessageEffect that indicates a failure as a result of
        the arguments being empty.
        """
        return error(
                _("Error Parsing %(op_code)s Arguments"), { 'op_code' : opcode },
                _("Must include a recognized language code."), {}
        )

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

PHONE_NUMBER = "\d{8}|\d{4}-\d{4}|\+\d{13}"
class UserRegistration(OperationBase):
    """Implements the SMS API for registering a new user."""
    helptext = "For example, %(opcode)s 12345678 Janice Smith. Creates a new user " + \
    "with phone number 12345678 and name Janice Smith"

    def _ok_phone(self, opcode, args):
        """
        Return a MessageEffect that indicates success.
        """
        return info(
            _("Parsed %(op_code)s Arguments"), { 'op_code' : opcode },
            _("Parsed: phone number to register is %(phone_number)s"), args
        )

    def _ok_phone_and_name(self, opcode, args):
        """
        Return a MessageEffect that indicates success.
        """
        return info(
            _("Parsed %(op_code)s Arguments"), { 'op_code' : opcode },
            _("Parsed: phone number to register for %(contact_name)s is %(phone_number)s"), args
        )

    def _error_invalid_phone_number(self, opcode, arg_string):
        """
        Return a MessageEffect that indicates a failure as a result of
        the arguments containing unrecognized characters in the argument string
        instead of a phone number.
        """
        return error(
                _("Error Parsing %(op_code)s Arguments"), { 'op_code' : opcode },
                _("Should start with a properly formatted phone number."), {}
        )

    def _error_no_phone_number(self, opcode, arg_string):
        """
        Return a MessageEffect that indicates a failure as a result of
        the arguments being empty.
        """
        return error(
                _("Error Parsing %(op_code)s Arguments"), { 'op_code' : opcode },
                _("Must include a phone number to register for this new user."), {}
        )

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
                args['contact_name'] = remaining.strip() 
                effect = self._ok_phone_and_name(opcode, args)
            else:
                effect = self._ok_phone(opcode, args)

        return [effect], args

