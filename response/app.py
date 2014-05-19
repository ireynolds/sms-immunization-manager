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
        print "+++++++++++++++++++++++++++++"
        print "message.fields:"
        print message.fields
        print "+++++++++++++++++++++++++++++"


        # message effects will be in a list. sort by .operation_index (None sorted before zero) 
        
        # check for the group in the message fields. only send a response based on what group the message is in. 

        # check for 'effects' errors
        # this means there was an error from the overall parser
        for effect in message.fields['effects']:
            if effect.type

            #respond with the first one

        # check for other errors
        # this means there were errors in the parsing of each section

            #respond with the first one

        # if there are no errors, respond with a thanks!
