import logging
from rapidsms.apps.base import AppBase

CONFIRMATION_RESPONSE =

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
        urgentEffects = [];
        errorEffect = None;

        # sort effects by the index of the operation code in the original
        # message. The index None is assumed to apply to the parsing of the
        # operation codes themselves so it should be first.
        effects = sort(message.fields['operation_effects'], key=lambda effect: -1 if effect.operation_index == None else effect.operation_index)

        for effect in effects:
            if effect.priority = URGENT:
                # always send urgent responses:
                    urgentEffect.append(effect)

            elif effect.priority = ERROR:
                # send only the first error response
                errorResponse.append(effect)
                break

        # send the urgent responses
        message.respond(__unicode__(effect.get_desc())) for effect in effects


        if message.fields['group'] != PLACE_HOLDER_GROUP_TYPE
            if errorEffect == None
                # message.respond()
                # How to create a response, send it, and record that we did send it for the moderation app?

        # if there are no errors, respond with a thanks!
