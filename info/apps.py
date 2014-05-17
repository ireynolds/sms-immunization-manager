from utils.operations import OperationBase
from operation_parser.gobbler import Gobbler, OPCODE
from moderation.models import error_parse, ok_parse

class Help(OperationBase):
    '''
    Handles the HE operation.
    '''

    def _ok(self, opcode, args):
        '''Return a MessageEffect that indicates success.'''
        return ok_parse(opcode, 
            "Parsed: requested operation code is %(opcode)s.", args)

    def _error_extra_chars(self, opcode, arg_string):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments having extra chars after the requested opcode.
        '''
        return error_parse(opcode, arg_string, reason="Text after requested operation code not allowed.")

    def _error_unrecognized_chars(self, opcode, arg_string):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments containing unrecognized characters in the argument string
        instead of an opcode.
        '''
        return error_parse(opcode, arg_string, reason="Should start with a complete operation code.")

    def _error_no_opcode(self, opcode, arg_string):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments being empty.
        '''
        return error_parse(opcode, arg_string, reason="Must request a specific operation code.")

    def parse_arguments(self, opcode, arg_string, message):
        '''
        Implements OperationBase.parse_arguments.
        '''
        args = {}
        effects = []

        g = Gobbler(arg_string.upper())

        help_opcode = g.gobble(OPCODE)
        args['opcode'] = help_opcode

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

