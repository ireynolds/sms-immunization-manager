import logging
from rapidsms.apps.base import AppBase
from moderation.models import *
from django.utils.translation import override, ugettext_noop as _
from sim.settings import INFORMATION

DO_NOT_SEND_CONFIRMATION = [ INFORMATION ]

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
        #print message.fields['operation_effects']
        effects = sorted(message.fields['operation_effects'], key=lambda effect: -1 if effect.operation_index == None else effect.operation_index)

        # collect the effects that need a response sent
        #print effects
        urgentEffects = [ effect for effect in effects if effect.priority == URGENT ]
        errorEffects = self._selectErrors(effects)

        # send the urgent responses
        if urgentEffects:
            self._sendRepsponses(urgentEffects, message)

        # send the error responses
        if errorEffects:
            self._sendRepsponses(errorEffects, message, " Please fix and send again.")

        elif message.fields['group'] not in DO_NOT_SEND_CONFIRMATION:
            # there are no errors, and this message needs a response
            name = _("Confirmation Response Sent")
            desc = _("Thanks for your message.")
            response = info(name, {}, desc, {})
            complete_effect(response, message.logger_msg, RESPOND, None, '', True)

            message.fields['operation_effects'].append(response)

            # set translation language for response
            with override(message.connections[0].contact.language):
                message.respond(unicode(response.get_desc()))

    def _selectErrors(self, effects):
        """
        Gathers the first effect that has priority ERROR and was not generated
        during the COMMIT stage.
        """
        for effect in effects:
            if effect.priority == ERROR and effect.stage != COMMIT:
                # send only the first error response
                return [ effect ]

    def _sendRepsponses(self, effects, message, additional_message=""):
        """
        Sends a response message to the original sender and creates a message
        effect to document the interaction.
        """
        for effect in effects:
            # create a new effect for sending the response
            name = _("Response Sent")
            desc = _("Responded to sender.%s" % additional_message)
            response = info(name, {}, desc, {})
            complete_effect(response, message.logger_msg, RESPOND, None, '', False)

            # set translation language for response
            with override(message.connections[0].contact.language):

                msg_to_send = ugettext("%(description)s%(additional_message)s" % { 'description': unicode(effect.get_desc()), 'additional_message': additional_message })

                # send and record the effect
                message.respond(unicode(msg_to_send))
                message.fields['operation_effects'].append(response)

            effect.sent_as_response = True
            effect.save()