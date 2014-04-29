from sim.operations import OperationBase, filter_by_opcode

class FridgeFailure(OperationBase):
    """
    A stub implementation of this operation
    """

    @filter_by_opcode
    def handle(self, message):
        ops = message.fields['operations']
        
        if "NF" in ops:
            self.handle_nf(message, ops["NF"])

    def handle_nf(self, message, args):
        check_results, commit_results = self.send_signals(message=message,
                                                          fridge_code="a")

        if commit_results == None:
            message.respond("FridgeFailure stub failed! %s" % repr(check_results))
        else:
            message.respond("FridgeFailure stub succeeded!")