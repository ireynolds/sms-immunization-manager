import django.dispatch
from sim.operations import OperationBase, filter_by_opcode
from operation_parser import gobbler

# Regular Expressions for parsing the stock code and level
STOCK_CODE = "[A-z]+"
STOCK_LEVEL = "[0-9]+"
NOT_ALPHA_NUM = "[^A-z0-9]*"
STOCK_LEVEL_OP_CODE = "SL"
STOCK_OUT_OP_CODE = "SE"

def select_errors(check_results, commit_results):
    if commit_results == None:
        # there were errors in the check phase, commit never attempted
        # TODO: attach the errors to the message
        return [(receiver, return_value) for (receiver, return_value) in check_results if return_value != None]

    if any(commit_results):
        # check for errors from the commit phase
        # TODO: attach the errors to the message
        return [(receiver, return_value) for (receiver, return_value) in commit_results if return_value != None]

    # Implies that there were no errors found
    # TODO: attach a success messgae
    return None

class StockLevel(OperationBase):
    """
    Parses stock codes and inventory levels from the provided message and sends
    the check and commit signals to the registered listners.
    """
    @filter_by_opcode
    def handle(self, message):
        # parse a list of stock code followed by level
        text = message.fields['operations'][STOCK_LEVEL_OP_CODE]
        levels, remaining = gobbler.gobble_all(STOCK_CODE + NOT_ALPHA_NUM + STOCK_LEVEL, text)

        if len(remaining) > 0:
            # there are still characters remaining meaning there was a parsing failure

            #TODO: i18n for this error message
            message.errors = [("SL Parse", "OK until: %s" % remaining)]
            return None

        if levels == None:
            # could not parse any usefull information
            message.errors = [("SL Parse", "No stock levels found.")]
            return None

        # create a dictionary: stock code -> stock level
        levels = [ gobbler.gobble(STOCK_CODE, l) for l in levels ]
        stock_levels = { stock_code: int(stock_level) for stock_code, stock_level in levels }

        check_results, commit_results = self.send_signals(message=message,
                                                          stock_levels=stock_levels)
        message.errors = select_errors(check_results, commit_results)
        if message.errors == None:
            message.respond = "Thank you."

class StockOut(OperationBase):
    """
    Parses stock codes and inventory levels from the provided message and sends
    the check and commit signals to the registered listners.
    """

    @filter_by_opcode
    def handle(self, message):

        text = message.fields['operations'][STOCK_OUT_OP_CODE]
        codes, remaining = gobbler.gobble_all(STOCK_CODE, text)

        if len(remaining) > 0:
            # there are still characters remaining, meaning there was a parsing failure

            #TODO: i18n for this error message
            message.errors = [("SE Parse", "OK until: %s" % remaining)]
            return None

        if codes == None:
            # could not parse any usefull information
            message.errors = [("SE Parse", "No stock code found.")]
            return None

        # codes is a one element list containg the stock code
        stock_code = codes[0]

        check_results, commit_results = self.send_signals(message=message,
                                                          stock_code=stock_code)

        message.errors = select_errors(check_results, commit_results)