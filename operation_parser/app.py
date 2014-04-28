import logging
from django.conf import settings
from rapidsms.apps.base import AppBase
import gobbler

logger = logging.getLogger("rapidsms")

def disambiguate_o0(string):
    """
    Returns the given string with all instances of "o" and "O" replaced by 
    "0". Many non-English-speaking users use "o", "O", and "0" 
    interchangeably, and this function can be used to effectively treat all 
    "o" and "O" characters as "0". 
    """
    return string.replace("o", "0").replace("O", "0")

def _find_opcodes(text, opcodes):
    indices = []
    for opcode in opcodes:
        index = text.find(opcode)
        if index != -1:
            indices.append(index)
    return indices

class OperationParser(AppBase):
    """
    A RapidSMS app for parsing messages into multiple operations. Adds an 'operations' field to
    each message in the parse phase. This field is a dictionary mapping operation codes to strings
    containing the arguments for that operation.
    """

    def parse(self, message, opcodes=None):
        if not opcodes:
            opcodes = settings.SIM_OPERATION_CODES.keys()

        text = message.text
        text = gobbler.strip_delimiters(text)
        text = disambiguate_o0(text)
        text = text.upper()

        opcode_indices = _find_opcodes(text, opcodes)

        #
        # HACK ATTACK!!!!!!
        #
        # When the message does not lead with any opcode, that opcode is assumed
        # to be "FT". 
        #
        if 0 not in opcode_indices:
            text = "FT" + text
            opcode_indices = _find_opcodes(text, opcodes)

        starts = sorted(opcode_indices)
        ends = starts[1:] + [len(text)]
        bounds = zip(starts, ends)

        operations = []
        for start, end in bounds:
            operation = text[start:end]
            opcode = operation[:2]
            args = gobbler.strip_delimiters(operation[2:])
            operations.append( (opcode, args) )

        message.fields['operations'] = dict(operations)
        logger.debug("Parser detected operations: %s" % repr(operations))
