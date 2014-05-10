import logging
import django.dispatch
from django.conf import settings
from rapidsms.apps.base import AppBase

logger = logging.getLogger("rapidsms")

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
        every check signal succeeds (returns None). Returns a 2-tuple containing the results of the
        check and commit signals respectively. Each element of the returned tuple is a list of
        tuples containing a signal receiver and the value that receiver returned. If the commit
        signal was not sent the second element of the returned tuple is None.
        """
        logger.debug("StockOut: %s" % repr(self.__class__))
        logger.debug("StockOut id: %d" % id(self.__class__))
        check_results = check_signal.send_robust(sender=self.__class__, message=message, **kwargs)

        for receiver, return_value in check_results:
            if return_value != None:
                return (check_results, None)

        commit_results = commit_signal.send_robust(sender=self.__class__, message=message, **kwargs)
        return (check_results, commit_results)

    def select_errors(self, check_results, commit_results):
        """
        Takes the lists of errors from the check and commit phases and repackages them into
        a single list of errors with no None values. If there were no errors from either phase
        returns None.
        """
        if commit_results == None:
            # there were errors in the check phase, commit never attempted
            # TODO: attach the errors to the message
            return [(receiver, return_value) for (receiver, return_value) in check_results if return_value != None]

        if any(commit_results):
            # check for errors from the commit phase
            # TODO: attach the errors to the message
            return [(receiver, return_value) for (receiver, return_value) in commit_results if return_value != None]

        # Implies that there were no errors found
        return None


# Signals for the check and commit operation phases. The sender of these signals will always be the
# class of the OperationBase subclass that is signaling. Every signal contains a message parameter,
# however additional keyword arguments may be passed by senders. Senders must pass the same
# arguments to check_signal and commit_signal.
check_signal  = django.dispatch.Signal(providing_args=["message"])
commit_signal = django.dispatch.Signal(providing_args=["message"])

def filter_by_opcode(handle_func):
    """
    A decorator which surrounds the handle function of an OperationBase subclass. Filters out
    messages that do not contain an operation assigned to that OperationBase.
    """
    def decorated(func_self, msg):
        if 'operations' not in msg.fields:
            # This message has not been parsed, do nothing
            return False

        if len(set(msg.fields['operations'].keys()) & func_self.get_opcodes()) == 0:
            # This message does contain a matching opcode
            print "\n missing operations @@@@@@@@@@@@@@@@@@@@@\n"
            return False

        # Otherwise, this message contains a matching opcode
        return handle_func(func_self, msg)

    return decorated