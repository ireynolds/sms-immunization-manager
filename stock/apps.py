import django.dispatch
from sim.operations import OperationBase, filter_by_opcode
from operation_parser import gobbler

# Regular Expressions for parsing the stock code and level
STOCK_CODE = "[A-z]+"
STOCK_LEVEL = "[0-9]+"
STOCK_LEVEL_OP_CODE = "SL"
STOCK_OUT_OP_CODE = "SO"

class StockLevel(OperationBase):
    """
    Parses stock codes and inventory levels from the provided message and sends
    the check and commit signals to the registered listners.
    """
    @filter_by_opcode
    def handle(self, message):

        # parse a list of stock code followed by level
        text = message.fields['operations'][STOCK_LEVEL_OP_CODE]
        levels, remaining = gobbler.gobble_all(STOCK_CODE + STOCK_LEVEL, text)

        if len(remaining) > 0:
            # there are still characters remaining, meaning there was a parsing failure

            #TODO: i18n for this error message
            message.respond("Please try again. We understood everything until: %s" % remaining)
            return None

        # create a dictionary: stock code -> stock level
        stock_levels = map(lambda l: gobbler.gobble(STOCK_CODE, l), levels)
        stock_levels = dict(map(lambda (code, level): (code, int(level)), stock_levels))

        check_results, commit_results = self.send_signals(message=message,
                                                          stock_levels=stock_levels)
        if commit_results == None:
            # there were errors in the check phase, commit never attempted
            # TODO: Select the error with the highest priority and respond
            message.respond("Error with message. %s" % repr(check_results))
        # else:
        #     # sort all the errors that were found
        #     onlyErrors = filter(lambda r: r != None, commit_results)
        #     errors = sorted(onlyErrors, key=lambda e: e.severity, reverse=True)

        #     if len(errors) > 0:
        #         # respond with the error of the greatest severity
        #         message.respond(errors[0].text)

        #     else:
        #         # respond with a success

        #         #TODO: i18n for this success message
        #         message.respond("Thank you for your report.")

class StockOut(OperationBase):
    """
    Parses stock codes and inventory levels from the provided message and sends
    the check and commit signals to the registered listners.
    """

    @filter_by_opcode
    def handle(self, message):

        text = message.fields['operations'][STOCK_LEVEL_OP_CODE]
        codes, remaining = gobbler.gobble_all(STOCK_CODE, text)

        if len(remaining) > 0:
            # there are still characters remaining, meaning there was a parsing failure

            #TODO: i18n for this error message
            message.respond("Error with message. We understood everything until: %s" % remaining)
            return None

        stock_codes = set(map(lambda l: gobbler.gobble(STOCK_CODE, l), codes))

        check_results, commit_results = self.send_signals(message=message,
                                                          stock_code=A)

        if commit_results == None:
            message.respond("StockOut stub failed! %s" % repr(check_results))
        else:
            message.respond("StockOut stub succeeded!")