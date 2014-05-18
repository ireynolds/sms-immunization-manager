import logging
from rapidsms.apps.base import AppBase

class Responder(AppBase):
    """
    Responds to the message sender with an acknowledgment receipt or that an
    error was detected in the message they sent.
    """

    def cleanup(self, message):
        """
        Implements the RapidSMS "cleanup" stage. Given a message, sends a
        response to the sender.

        If no errors were detected in previous phases the response is a simple
        acknowledgment of receipt. If one or more errors were detected response
        sent will describe the error of highest priority.
        """
        print message.fields['operations']
        print message.fields['effects']