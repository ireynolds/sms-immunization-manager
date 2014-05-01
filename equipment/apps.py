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

class EquipmentBase(OperationBase):

    def _take_at_most_one_equipment_id(self, args):
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

    def _respond_to_error(self, message, check_results, commit_results):
        # Send appropriate response (including the highest-priority error returned in check or commit phases)
        results = check_results + (commit_results if commit_results else [])
        if _has_errors(results):
            return str(_top_error(results))
        else:
            return "Success. Thanks for your input!"

    def _handle_any(self, message, opcode):
        args = message.fields['operations'][opcode]

        try:
            equipment_id = self._take_at_most_one_equipment_id(args)
        except (TooManyArgsException, UnrecognizedTextException) as e:
            message.respond(str(e))
            return

        check_results, commit_results = self.send_signals(message=message,
                                                          equipment_id=equipment_id)

        error = self._respond_to_error(message, check_results, commit_results)
        message.respond(str(error))

class EquipmentFailure(EquipmentBase):

    @filter_by_opcode
    def handle(self, message):
        self._handle_any(message, "NF")      

class EquipmentRepaired(EquipmentBase):

    @filter_by_opcode
    def handle(self, message):
        self._handle_any(message, "WO")