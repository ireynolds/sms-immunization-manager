from sim.operations import OperationBase, filter_by_opcode

from operation_parser.gobbler import *

def _top_error(results):
    return _errors(results)[0][1]

def _errors(results):
    return filter(lambda e: e[1] != None, results)

def _has_errors(results):
    return len(_errors(results)) > 0

class TooManyArgsException(Exception):
    pass

class UnrecognizedTextException(Exception):
    pass

def _take_at_most_one_equipment_id(args):
    equipment_id, remaining = gobble("[A-Z]", args.upper())
    # It's okay if equipment_id is None--this is within spec.

    # Extra stuff--reject with error
    if remaining:
        if equipment_id:
            error = "Message OK until %s. Provide one equipment code and nothing else. " \
                    "Please fix and send again." % (remaining[:3],)
            raise TooManyArgsException(error)
        else:
            error = "Message OK until %s. Expected an equipment code. Please fix and " \
                    "send again." % (remaining[:3],)
            raise UnrecognizedTextException(error)
        message.respond(response)

    return equipment_id

class EquipmentFailure(OperationBase):

    @filter_by_opcode
    def handle(self, message):
        args = message.fields['operations']["NF"]

        try:
            equipment_id = _take_at_most_one_equipment_id(args)
        except (TooManyArgsException, UnrecognizedTextException) as e:
            message.respond(str(e))
            return

        check_results, commit_results = self.send_signals(message=message,
                                                          equipment_id=equipment_id)

        # Send appropriate response (including the highest-priority error returned in check or commit phases)
        results = check_results + (commit_results if commit_results else [])
        if _has_errors(results):
            message.respond(str(_top_error(results)))
        else:
            message.respond("Success. Thanks for your input!")

class EquipmentRepaired(OperationBase):

    @filter_by_opcode
    def handle(self, message):
        pass