import logging
from rapidsms.apps.base import AppBase
from moderation.models import *

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

        # sort effects by the index of the operation code in the original
        # message. The index None is assumed to apply to the parsing of the
        # operation codes themselves so it should be first.
        print message.fields['operation_effects']
        effects = sorted(message.fields['operation_effects'], key=lambda effect: -1 if effect.operation_index == None else effect.operation_index)

        # collect the effects that need a response sent
        print effects
        urgentEffects = [ effect for effect in effects if effect.priority == URGENT ]
        errorEffects = self._selectErrors(effects)

        # send the urgent responses
        if urgentEffects:
            self._sendRepsponses(urgentEffects, message)

        # send the error responses
        if errorEffects:
            self._sendRepsponses(errorEffects, message)

        else:
            # there are no errors, respond with a thanks!
            name = "Confirmation Response Sent"
            desc = "Thanks for your message."
            response = info(name, {}, desc, {})
            complete_effect(response, message, RESPOND, None, '', True)

            msg.fields['operation_effects'].append(effect)

            message.respond(__unicode__(response.get_desc()))


    def _selectErrors(self, effects):
        for effect in effects:
            if effect.priority == ERROR:
                # send only the first error response
                return [ effect ]

    def _sendRepsponses(self, effects, message):
        for effect in effects:
            message.respond(__unicode__(effect.get_desc()))
            effect.sent_as_response = True
            effect.save()