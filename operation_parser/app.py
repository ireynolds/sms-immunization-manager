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
        opcodes = settings.SIM_OPERATION_CODES.keys()

        # For now, pretend the message has the following operations:
        operations = {
            "SL": "StockLevelParamsGoHere",
            "SO": "StockOutParamsGoHere",
            "FF": "FridgeFailureParamsGoHere",
        }

        message.fields['operations'] = operations
        logger.debug("Parser detected operations: %s" % repr(operations))
