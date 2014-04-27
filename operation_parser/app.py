import logging
from django.conf import settings
from rapidsms.apps.base import AppBase

logger = logging.getLogger("rapidsms")

class OperationParser(AppBase):
    """
    A RapidSMS app for parsing messages into multiple operations. Adds an 'operations' field to
    each message in the parse phase. This field is a dictionary mapping operation codes to strings
    containing the arguments for that operation.

    This implementation is a stub, and should be replaced.
    """

    def parse(self, message):
        # This will be necessary later, when the parser recognizes invalid opcodes.
        opcodes = settings.SIM_OPERATION_CODES.keys()

        text = message.text.strip()

        # For now, the parser merely assumes one operation, prefaced by an 
        # arbitrary argument string.
        opcode = text[:2]
        args = text[2:].strip()
        operations = { opcode: args }

        message.fields['operations'] = operations
        logger.debug("Parser detected operations: %s" % repr(operations))
