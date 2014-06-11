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
        i = 0
        while i < len(text) - 1:
            possible_opcode = text[i:i + 2]
            if possible_opcode in opcodes:
                indices.append(i)
                i += 1
            i += 1

        # settings.SIM_OPCODES_MUST_APPEAR_LAST opcodes must come last and may 
        # not appear together. Thus, find the first instance of RG or HE and 
        # treat remove all following "opcodes" because they are, in fact, part 
        # of the arguments to RG or HE.
        indices = sorted(indices)
        i = 0
        while i < len(indices):
            index = indices[i]
            if text[index:index + 2] in settings.SIM_OPCODES_MUST_APPEAR_LAST:
                del indices[i + 1:]
            i += 1

        return indices

    def _get_operations(self, text, opcodes, message):
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
            if opcode in settings.SIM_OPCODES_PASS_ORIGINAL_ARGS:
                arg_string = message.text[start + 2:end]
            else:
                arg_string = operation[2:]
            args = gobbler.strip_delimiters(arg_string)

            operations.append( (opcode, args) )

        return operations

    def _ok_effect(self, operations, message):
        '''
        Returns a completed INFO effect that describes the given operations that
        were parsed from the given message.
        '''
        result_fmtstr = _("Parser detected operations: %(ops)s")
        result_context = {"ops": ', '.join(operations)}
        effect = info(_("Parsed Operation Codes"), {}, result_fmtstr, result_context)
        return complete_effect(effect, message.logger_msg, SYNTAX)

    def _if_contains_ops_from_multiple_groups(self, operations, message):
        # Remove contextual opcodes
        opcodes = [opcode for opcode, _ in operations if settings.SIM_OPCODE_GROUPS[opcode] != settings.CONTEXTUAL]

        if len(opcodes) == 0:
            return

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
            return

        effect = error(
            "Error Verifying Operation Codes", 
                {},
            "Cannot include %(opcode)s and %(conflicting_opcode)s in the same message.", 
                { "opcode": opcode0, "conflicting_opcode": conflicting_opcode }
        )
        return complete_effect(effect, message.logger_msg, SYNTAX, operation_index=None)

    def _if_contains_disallowed_repeated_op(self, operations, message):
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
            return

        effect = error(
            "Error Verifying Operation Codes", 
                {},
            "Cannot include %(duplicated_opcode)s more than once in the same message.", 
                { "duplicated_opcode": duplicated_opcode }
        )
        return complete_effect(effect, message.logger_msg, SYNTAX, operation_index=None)

    def _if_contains_only_contextual(self, operations, message):
        non_contextual = None
        for opcode, _ in operations:
            if settings.SIM_OPCODE_GROUPS[opcode] != settings.CONTEXTUAL:
                non_contextual = opcode
                break

        if non_contextual:
            return

        effect = error(
            "Error Verifying Operation Codes", 
                {},
            "Message must submit or request information.", 
                {}
        )
        return complete_effect(effect, message.logger_msg, SYNTAX, operation_index=None)

    def _group(self, operations):
        group = None
        for opcode, _ in operations:
            this_group = settings.SIM_OPCODE_GROUPS[opcode]
            if this_group != settings.CONTEXTUAL:
                group = this_group
                break

        return group

    def parse(self, message):
        '''
        Implements the RapidSMS "parse" stage. Given a message, returns a list 
        of pairs of opcodes and their corresponding arguments in the order they 
        appear in the message.

        Also disambiguates between "o" and "0" by replacing all "o" with "0". Assumes 
        that opcodes are uppercase and converts the message text to uppercase.

        Returned arguments have had delimiters stripped from front and back.
        '''
        text = disambiguate_o0(message.text.upper())
        operations = self._get_operations(text, settings.SIM_OPERATION_CODES.keys(), message)

        # Check for errors between all operations
        effects = []
        effects.append(self._if_contains_ops_from_multiple_groups(operations, message))
        effects.append(self._if_contains_disallowed_repeated_op(operations, message))
        effects.append(self._if_contains_only_contextual(operations, message))
        effects = filter(None, effects)
        if len(effects) == 0:
            opcodes = [opcode for opcode, _ in operations]
            effects = [self._ok_effect(opcodes, message)]

        message.fields['group'] = self._group(operations)
        message.fields['operations'] = operations
        message.fields['operation_effects'] = effects

        logger.debug("Parser detected operations: %s" % repr(operations))
