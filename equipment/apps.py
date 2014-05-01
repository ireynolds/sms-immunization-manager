from sim.operations import OperationBase, filter_by_opcode

from operation_parser.gobbler import *

def _top_error(results):
    return _errors(results)[0][1]

def _errors(results):
    return filter(lambda e: e[1] != None, results)

def _has_errors(results):
    return len(_errors(results)) > 0

class EquipmentFailure(OperationBase):

    @filter_by_opcode
    def handle(self, message):
        equipment_id, remaining = gobble("[A-Z]", message.fields['operations']["NF"].upper())
        # It's okay if equipment_id is None--this is within spec.

        # Extra stuff--reject with error
        if remaining:
            if equipment_id:
                response = "Message OK until %s. Provide one equipment code and nothing else. Please fix and send again." % (remaining[:3],)
            else:
                response = "Message OK until %s. Expected an equipment code. Please fix and send again." % (remaining[:3],)
            message.respond(response)
            return

        check_results, commit_results = self.send_signals(message=message,
                                                          equipment_id=equipment_id)

        # Send appropriate response (including the highest-priority error returned in check or commit phases)
        results = check_results + (commit_results if commit_results else [])
        if _has_errors(results):
            message.respond(str(_top_error(results)))
        else:
            message.respond("Success. Thanks for your input!")

