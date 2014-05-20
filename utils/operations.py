import traceback
import django.dispatch
from django.conf import settings
from django.utils.translation import ugettext_noop as _
from rapidsms.apps.base import AppBase
from moderation.models import *
from registration.models import *

# Define which priorities halt message processing
HALTING_PRIORITIES = set([ERROR])

class OperationBase(AppBase):
    """
    A RapidSMS app that implements an operation code. Subclasses must implement parse_operation.
    """

    def parse_arguments(self, opcode, arg_string, message):
        """
        Parses the given message into a Python representation of its syntactical meaning. Returns
        a 2-tuple containing a list of MessageEffects representing the results of the parsing, and a
        Python dictionary with keyword arguments to be sent to semantic and commit signal receivers
        (in addition to a 'message' argument that is automatically sent).

        Must be implemented by subclasses of OperationBase.
        """
        raise NotImplementedError("parse_message must be implemented by OperationBase subclasses")

    def parse(self, message):
        """
        Implements RapidSMS' parse phase. Adds a field 'operation_arguments' to message containing
        the parsed syntax of the operation, and a field 'operation_effects' which logs the effects
        of message processing. If parsing is successful, sends the semantic signal and logs its
        effects.
        """

        if "operation_arguments" not in message.fields:
            message.fields["operation_arguments"] = [None] * len(message.fields["operations"])

        if "operation_effects" not in message.fields:
            message.fields["operation_effects"] = []

        # Examine each operation in the message to determine if it should be parsed
        for index in xrange(len(message.fields["operations"])):
            opcode, argstring = message.fields["operations"][index] 

            # Skip opcodes that don't apply to us
            if opcode not in self.get_opcodes():
                continue

            # Parse the arguments
            effects, kwargs = self.parse_arguments(opcode, argstring, message)
            message.fields["operation_arguments"][index] = kwargs

            # Complete any effects from parsing arguments
            for effect in effects:
                complete_effect(effect, message.logger_msg, SYNTAX, index, opcode)
            message.fields["operation_effects"].extend(effects)

            # Do not run semantic checks if the syntax checks failed
            if self._should_halt(effects):
                continue

            # If no parsing effects were halting, send the semantic signal
            responses = semantic_signal.send_robust(sender=self.__class__,
                                                    message=message,
                                                    opcode=opcode,
                                                    **kwargs)
            self._handle_signal_responses(responses, SEMANTIC, message, index, opcode)

    def handle(self, message):
        """
        Implements RapidSMS' handle phase. If no halting errors have occured in previous phases,
        sends the commit signal and logs the results. Always returns False to allow other RapidSMS
        apps an opportunity to handle the message.
        """
        if self._should_halt(message.fields["operation_effects"]):
            return False

        # Examine each operation in the message to determine if it should be handled
        for index in xrange(len(message.fields["operations"])):
            opcode, argstring = message.fields["operations"][index]
            kwargs = message.fields["operation_arguments"][index]

            if opcode in self.get_opcodes():
                responses = commit_signal.send_robust(sender=self.__class__,
                                                      message=message,
                                                      opcode=opcode,
                                                      **kwargs)
                self._handle_signal_responses(responses, COMMIT, message, index, opcode)
        
        return False

    def get_opcodes(self):
        """
        Returns the set of operation codes associated with this operation.
        """
        result = set()
        for opcode, appbase in settings.SIM_OPERATION_CODES.iteritems():
            if appbase == self.__class__:
                result.add(opcode)
        return result

    def _should_halt(self, effects):
        """
        Returns whether processing of the given message should be halted on account of an error in
        a previous stage.
        """
        for effect in effects:
            if effect.priority in HALTING_PRIORITIES:
                return True
        return False

    def _handle_signal_responses(self, signal_responses, stage, message, index, opcode):
        """
        Helper function to handle responses from signal receivers.
        """
        for receiver, effects_or_exception in signal_responses:
            for effect in self._check_for_exception(effects_or_exception, receiver):
                complete_effect(effect, message.logger_msg, stage, index, opcode)
                message.fields["operation_effects"].append(effect)

    def _check_for_exception(self, effects_or_exception, receiver):
        """
        Checks if the given signal result is an exception or an effect. If it is an exception,
        returns a list of MessageEffects describing the exception. Otherwise, returns
        effects_or_exception.
        """
        if not isinstance(effects_or_exception, Exception):
            # No exception was raised, return the list of effects
            return effects_or_exception

        # Create a developer-visible (debug) effect documenting the exception's traceback
        exception = effects_or_exception
        name = _("Signal receiver '%(receiver)s' raised exception")
        name_context = {'receiver': repr(receiver)}
        desc = _("Traceback:\n%(traceback)s")
        desc_context = {'traceback': traceback.format_exc(exception)}
        debug_effect = debug(name, name_context, desc, desc_context)

        # Create a user-visible effect documenting that an internal error occured
        name = _("Internal error")
        desc = _("An internal error occured when processing your request")
        error_effect = error(name, {}, desc, {})

        return [debug_effect, error_effect]


# Signals for the semantic and commit stages. The sender of these signals will always be the class
# of the OperationBase subclass that is signaling. Every signal contains a message parameter,
# however additional keyword arguments may be passed by senders. Senders must pass the same
# arguments to both signals. Receivers of these signals must return a list containing at least one
# MessageEffect instance created using moderation.models.create_effect or one of its shortcut
# functions.
semantic_signal  = django.dispatch.Signal(providing_args=["message", "opcode"])
commit_signal = django.dispatch.Signal(providing_args=["message", "opcode"])
