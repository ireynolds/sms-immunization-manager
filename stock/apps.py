import django.dispatch
from sim.operations import OperationBase, filter_by_opcode

class StockLevel(OperationBase):
    """
    A stub implementation of this operation
    """

    @filter_by_opcode
    def handle(self, message):
        check_results, commit_results = self.send_signals(message=message,
                                                          stock_levels={'a': 1, 'b': 2})

        if commit_results == None:
            message.respond("StockLevel stub failed! %s" % repr(check_results))
        else:
            message.respond("StockLevel stub succeeded!")

class StockOut(OperationBase):
    """
    A stub implementation of this operation
    """

    @filter_by_opcode
    def handle(self, message):
        check_results, commit_results = self.send_signals(message=message,
                                                          stock_code="a")

        if commit_results == None:
            message.respond("StockOut stub failed! %s" % repr(check_results))
        else:
            message.respond("StockOut stub succeeded!")