import logging
from django.conf import settings
from rapidsms.apps.base import AppBase
import gobbler
from moderation.models import *
from django.utils.translation import ugettext_noop as _

logger = logging.getLogger("rapidsms")

def disambiguate_o0(string):
    '''
    Returns the given string with all instances of "o" and "O" replaced by 
    "0". Used to address non-English-speakers' confusion between those characters.
    '''
    return string.replace("o", "0").replace("O", "0")

class OperationParser(AppBase):
    '''
    Parses an incoming message into its constituent operations and their 
    argument strings. Defines a RapidSMS "parse" phase that is executes
    before any other app's parse phase.
    '''

    def _find_opcodes(self, text, opcodes):
        '''
        given a string of the form [${OPCODE}${ARGUMENTS}]+, returns a sorted list
        of the indices of each opcode.
        '''
        indices = []
        for opcode in opcodes:            
            index = 0
            while True:
                index = text.find(opcode, index)
                if index == -1:
                    break
                indices.append(index)
                index += 2

        return indices

    def _get_operations(self, text, opcodes):
        '''
        Given the text of a message (in the form [${OPCODE}${ARGUMENTS}]+) and a list 
        of valid opcodes, returns a sorted list of pair (opcode, arguments). 

        The arguments have had delimiters stripped from their front and back.
        '''

        opcode_indices = self._find_opcodes(text, opcodes)
        
        starts = sorted(opcode_indices)
        ends = starts[1:] + [len(text)]
        bounds = zip(starts, ends)

        operations = []
        for start, end in bounds:
            operation = text[start:end]

            opcode = operation[:2]
            args = gobbler.strip_delimiters(operation[2:])

            operations.append( (opcode, args) )

        return operations

    def _ok_effect(self, operations, message):
        '''
        Returns a completed INFO effect that describes the given operations that
        were parsed from the given message.
        '''
        result_fmtstr = _("Parser detected operations: %(ops)s")
        result_context = {"ops": repr(operations)}
        effect = info(_("Parsed Operation Codes"), {}, result_fmtstr, result_context)
        return complete_effect(effect, message.logger_msg, SYNTAX)

    def _contains_ops_from_multiple_groups(self, operations, message):
        # Remove contextual opcodes
        opcodes = [opcode for opcode, _ in operations if settings.SIM_OPCODE_GROUPS[opcode] != settings.CONTEXTUAL]

        # Get the first opcode and its group
        opcode0 = opcodes[0]
        conflicting_opcode = None
        group = settings.SIM_OPCODE_GROUPS[opcode0]

        # Scan through the rest and store the first opcode that has a different
        # group (or None)
        for this_opcode in opcodes[1:]:
            this_group = settings.SIM_OPCODE_GROUPS[this_opcode]

            if this_group != group:
                conflicting_opcode = this_opcode
                break

        # See if we found a conflicting opcode
        if not conflicting_opcode:
            return None

        effect = error(
            "Error Verifying Operation Codes", 
                {},
            "Error. Cannot include %(opcode)s and %(conflicting_opcode)s in the same message. Please fix and try again.", 
                { "opcode": opcode0, "conflicting_opcode": conflicting_opcode }
        )
        return complete_effect(effect, message.logger_msg, SYNTAX, operation_index=None)

    def _contains_disallowed_repeated_op(self, operations, message):
        only_once_opcodes = set(settings.SIM_OPCODE_MAY_NOT_DUPLICATE)
        opcodes = [opcode for opcode, _ in operations if opcode in settings.SIM_OPCODE_MAY_NOT_DUPLICATE]

        duplicated_opcode = None
        for opcode in opcodes:
            if opcode in only_once_opcodes:
                only_once_opcodes.remove(opcode)
            else:
                duplicated_opcode = opcode
                break

        if not duplicated_opcode:
            return None

        effect = error(
            "Error Verifying Operation Codes", 
                {},
            "Error. Cannot include %(duplicated_opcode)s more than once in the same message. Please fix and try again.", 
                { "duplicated_opcode": duplicated_opcode }
        )
        return complete_effect(effect, message.logger_msg, SYNTAX, operation_index=None)


    def parse(self, message, opcodes=None):
        '''
        Implements the RapidSMS "parse" stage. Given a message (and, optionally, a 
        list of valid opcodes), returns  a list of pairs of opcodes and their 
        corresponding arguments in the order they appear in the message.

        Also disambiguates between "o" and "0" by replacing all "o" with "0". Assumes 
        that opcodes are uppercase and converts the message text to uppercase.

        Returned arguments have had delimiters stripped from front and back.
        '''
        if not opcodes:
            opcodes = settings.SIM_OPERATION_CODES.keys()

        text = disambiguate_o0(gobbler.strip_delimiters(message.text).upper())
        operations = self._get_operations(text, opcodes)

        # Check for errors between all operations
        effects = []
        effects.append(self._contains_ops_from_multiple_groups(operations, message))
        effects.append(self._contains_disallowed_repeated_op(operations, message))
        effects = filter(None, effects)

        if len(effects) == 0:
            effects = [self._ok_effect(operations, message)]

        message.fields['operations'] = operations
        message.fields['operation_effects'] = effects

        logger.debug("Parser detected operations: %s" % repr(operations))
