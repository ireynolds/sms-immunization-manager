from django.dispatch.dispatcher import receiver
from utils.operations import OperationBase, semantic_signal, commit_signal
from operation_parser.gobbler import Gobbler, OPCODE
from moderation.models import urgent, error, info
from django.conf import settings
from django.utils.translation import ugettext_noop as _

class Help(OperationBase):
    '''
    Handles the HE operation.
    '''

    helptext = "For example, %(opcode)s SL. Returns information about a given operation."

    def _ok(self, opcode, args):
        '''Return a MessageEffect that indicates success.'''
        return info(
            _("Parsed %(op_code)s Arguments"), { 'op_code': opcode },
            _("Parsed: requested operation code is %(requested_opcode)s."), args
        )

    def _error_extra_chars(self, opcode, arg_string):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments having extra chars after the requested opcode.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Text after requested operation code not allowed."), {}
        )

    def _error_unrecognized_chars(self, opcode, arg_string):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments containing unrecognized characters in the argument string
        instead of an opcode.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Should start with a complete operation code."), {}
        )

    def _error_no_opcode(self, opcode, arg_string):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments being empty.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Must request a specific operation code."), {}
        )

    def parse_arguments(self, opcode, arg_string, message):
        '''
        Implements OperationBase.parse_arguments.
        '''
        args = {}
        effects = []

        g = Gobbler(arg_string.upper())

        help_opcode = g.gobble(OPCODE)
        args['requested_opcode'] = help_opcode

        if help_opcode:
            if g.remainder:
                args, effect = None, self._error_extra_chars(opcode, arg_string)
            else:
                args, effect = args, self._ok(opcode, args)
        else:
            if g.remainder:
                args, effect = None, self._error_unrecognized_chars(opcode, arg_string)
            else:
                args, effect = None, self._error_no_opcode(opcode, arg_string)
        effects.append(effect)

        return (effects, args)

@receiver(semantic_signal, sender=Help)
def help_semantic(sender, message, opcode, requested_opcode, **named_args):
    if requested_opcode not in settings.SIM_OPERATION_CODES.keys():
        effect = error(
            _("Error Interpreting %(op_code)s Arguments"), { 'op_code': opcode},
            _("Requested help for unrecognized operation %(requested_opcode)s."), { 'requested_opcode': requested_opcode }            
        )
    else:
        effect = info(
            _("Verified %(op_code)s Arguments"), { 'op_code': opcode },
            _("Requested help for operation %(requested_opcode)s."), { 'requested_opcode': requested_opcode }
        )

    return [effect]

@receiver(commit_signal, sender=Help)
def help_commit(sender, message, opcode, requested_opcode, **named_args):
    effect = urgent(
        "Information about %(opcode)s", { 'opcode': requested_opcode },
        settings.SIM_OPERATION_CODES[requested_opcode].helptext, { 'opcode': requested_opcode }
    )
    return [effect]