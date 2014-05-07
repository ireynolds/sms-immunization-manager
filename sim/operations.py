import django.dispatch
from django.conf import settings
from rapidsms.apps.base import AppBase

class OperationBase(AppBase):
    """
    A RapidSMS app that implements an operation code.
    """

    def get_opcodes(self):
        """
        Returns the set of operation codes associated with this operation.
        """
        result = set()
        for opcode, appbase in settings.SIM_OPERATION_CODES.iteritems():
            if appbase == self.__class__:
                result.add(opcode)

        return result

    def send_signals(self, message, **kwargs):
        """
        Sends this operation's signals with the given parameters. Only sends the commit signal if
        every check signal succeeds. Returns a 2-tuple containing the results of the check and
        commit signals respectively. Each element of the returned tuple is a list of tuples
        containing a signal receiver and the instance of MessageEffect returned by the receiver. If
        the commit signal was not sent the second element of the returned tuple is None.
        """
        check_effects = check_signal.send_robust(sender=self.__class__, message=message, **kwargs)

        # Update and save the message effects returned by the check signal receivers
        # TODO: Handle if a receiver returns an exception instead of a MessageEffect (also do the
        # same for the commit phase)
        check_failed = False
        for receiver, message_effect in check_effects:
            message_effect.check_phase = True
            message_effect.message = message.logger_msg
            message_effect.save()

            check_failed = check_failed or not message_effect.success

        # If a check failed, return without sending the commit signal
        if check_failed:
            return (check_effects, None)

        commit_effects = commit_signal.send_robust(sender=self.__class__, message=message, **kwargs)

        # Update and save the message effects returned by the commit signal receivers
        check_failed = False
        for receiver, message_effect in commit_effects:
            message_effect.check_phase = False
            message_effect.message = message.logger_msg
            message_effect.save()

        return (check_effects, commit_effects)


# Signals for the check and commit operation phases. The sender of these signals will always be the
# class of the OperationBase subclass that is signaling. Every signal contains a message parameter,
# however additional keyword arguments may be passed by senders. Senders must pass the same
# arguments to check_signal and commit_signal. These signals should only be sent by calling
# OperationBase.send_signals.
check_signal  = django.dispatch.Signal(providing_args=["message"])
commit_signal = django.dispatch.Signal(providing_args=["message"])

def filter_by_opcode(handle_func):
    """
    A decorator which surrounds any RapidSMS phase function (e.g. parse, handle) of an OperationBase
    subclass. Filters out messages that do not contain an operation assigned to that OperationBase.
    """
    def decorated(func_self, msg):
        if 'operations' not in msg.fields:
            # This message has not been parsed, do nothing
            return False

        if len(set(msg.fields['operations'].keys()) & func_self.get_opcodes()) == 0:
            # This message does contain a matching opcode
            return False

        # Otherwise, this message contains a matching opcode
        return handle_func(func_self, msg)

    return decorated