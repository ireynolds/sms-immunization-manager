import django.dispatch
from sim.operations import OperationBase, filter_by_opcode
from operation_parser import gobbler

# Regular Expressions for parsing the stock code and level
STOCK_CODE = "[A-z]+"
STOCK_LEVEL = "[0-9]+"
STOCK_LEVEL_OP_CODE = "SL"
STOCK_OUT_OP_CODE = "SE"

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

        if len(remaining) > 0 or levels == ():
            # there are still characters remaining, meaning there was a parsing failure

            #TODO: i18n for this error message
            message.respond("Please try again. We understood everything until: %s" % remaining)
            return None

        # levels = map(lambda l: gobbler.gobble(STOCK_CODE, l), levels)
        # stock_levels = dict(map(lambda (code, level): (code, int(level)), levels))

        # create a dictionary: stock code -> stock level
        levels = [ gobbler.gobble(STOCK_CODE, l) for l in levels ]
        stock_levels = { first: int(second) for first, second in levels }

        check_results, commit_results = self.send_signals(message=message,
                                                          stock_levels=stock_levels)
        if commit_results == None:
            # there were errors in the check phase, commit never attempted
            # TODO: attach the errors to the message

            return None

        if not all(r is None for r in check_results):
            # check for errors from the commit phase
            # TODO: attach the errors to the message

            return None

        # Implies that there were no errors found
        # TODO: attach a success messgae
        return None

class StockOut(OperationBase):
    """
    Parses stock codes and inventory levels from the provided message and sends
    the check and commit signals to the registered listners.
    """

    @filter_by_opcode
    def handle(self, message):

        text = message.fields['operations'][STOCK_OUT_OP_CODE]
        codes, remaining = gobbler.gobble_all(STOCK_CODE, text)

        if len(remaining) > 0 or codes == None:
            # there are still characters remaining, meaning there was a parsing failure

            #TODO: i18n for this error message
            message.respond("Error with message. We understood everything until: %s" % remaining)
            return None

        # TODO: Should this accept more than one stock code per message?
        # Either way rewrite the parsing to make this statement more clear
        stock_code = codes[0][0]

        check_results, commit_results = self.send_signals(message=message,
                                                          stock_code=stock_code)

        if commit_results == None:
            # there were errors in the check phase, commit never attempted
            # TODO: attach the errors to the message

            return None

        if not all(r is None for r in check_results):
            # check for errors from the commit phase
            # TODO: attach the errors to the message

            return None

        # Implies that there were no errors found
        # TODO: attach a success messgae
        return None