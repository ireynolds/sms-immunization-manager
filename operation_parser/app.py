import logging
from django.conf import settings
from rapidsms.apps.base import AppBase
import gobbler
from moderation.models import *
from django.utils.translation import ugettext_noop as _

logger = logging.getLogger("rapidsms")

def disambiguate_o0(string):
    """
    Returns the given string with all instances of "o" and "O" replaced by 
    "0". Many non-English-speaking users use "o", "O", and "0" 
    interchangeably, and this function can be used to effectively treat all 
    "o" and "O" characters as "0". 
    """
    return string.replace("o", "0").replace("O", "0")

class OperationParser(AppBase):

    def _find_opcodes(self, text, opcodes):
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
        opcode_indices = self._find_opcodes(text, opcodes)

        ##########

        # HACK ATTACK!!!!!!
        # When the message does not lead with any opcode, that opcode is assumed
        # to be "FT". 
        if 0 not in opcode_indices:
            text = "FT" + text
            opcode_indices = self._find_opcodes(text, opcodes)

        ##########

        starts = sorted(opcode_indices)
        ends = starts[1:] + [len(text)]
        bounds = zip(starts, ends)

        operations = []
        for start, end in bounds:
            operation = text[start:end]

            opcode = operation[:2]
            args = gobbler.strip_delimiters(operation[2:])
            args = disambiguate_o0(args)

            operations.append( (opcode, args) )

        return operations

    def _get_complete_effects(self, operations, message):
        result_fmtstr = _("Parser detected operations: %(ops)s")
        result_context = {"ops": repr(operations)}
        effect = info(_("Parsed Operation Codes"), {}, result_fmtstr, result_context)
        return complete_effect(effect, message.logger_msg, SYNTAX)

    def parse(self, message, opcodes=None):
        if not opcodes:
            opcodes = settings.SIM_OPERATION_CODES.keys()

        text = gobbler.strip_delimiters(message.text).upper()
        operations = self._get_operations(text, opcodes)        
        effect = self._get_complete_effects(operations, message)

        message.fields['operations'] = operations
        message.fields['effects'] = [effect]

        logger.debug("Parser detected operations: %s" % repr(operations))
