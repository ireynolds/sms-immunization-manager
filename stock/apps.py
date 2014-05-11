import django.dispatch
from sim.operations import OperationBase
from operation_parser import gobbler
from moderation.models import *
from django.utils.translation import ugettext_noop as _

# Regular Expressions for parsing the stock code and level
STOCK_CODE = "[A-z]+"
STOCK_LEVEL = "[0-9]+"
NOT_ALPHA_NUM = "[^A-z0-9]*"
STOCK_LEVEL_OP_CODE = "SL"
STOCK_OUT_OP_CODE = "SE"

class StockLevel(OperationBase):

    def parse_arguments(self, arg_string, message):
        """
        Parses stock codes and inventory levels from the provided argument string.
        Expects one or more of the format: <Stock Code> <Inventory Level>
        Returns a 2-tuple containing a list of MessageEffects representing the
        results of the parsing, and a Python dictionary mapping the stock code
        strings to integer inventory levels.
        """
        levels, remaining = gobbler.gobble_all(STOCK_CODE + NOT_ALPHA_NUM + STOCK_LEVEL, arg_string)

        if len(remaining) > 0:
            # there are still characters remaining, meaning there was a parsing failure
            result_fmtstr = _("OK until: %(remaining_chars)s. " \
                                "Please fix and send again.")
            result_context = { "remaining_chars": remaining }

            effect = error(_("Error Parsing " + STOCK_LEVEL_OP_CODE + " Arguments"), {}, result_fmtstr, result_context)
            return [effect], {}

        if levels == None:
            # did not find any stock code and level combos
            result_fmtstr = _("OK until: %(remaining_chars)s. Did not find any stock levels." \
                                "Please fix and send again.")
            result_context = { "remaining_chars": remaining }

            effect = error(_("Error Parsing " + STOCK_LEVEL_OP_CODE + " Arguments"), {}, result_fmtstr, result_context)
            return [effect], {}

        # create a dictionary: stock code -> stock level
        levels = [ gobbler.gobble(STOCK_CODE, l) for l in levels ]
        stock_levels = {}

        for stock_code, stock_level in levels:
            if stock_code in stock_levels:
                # there was a duplicate stock code in the message
                result_fmtstr = _("%(dup_stock_code)s Appeared in the message more than once." \
                                "Please fix and send again.")
                result_context = { "dup_stock_code": stock_code }

                effect = error(_("Error Parsing " + STOCK_LEVEL_OP_CODE + " Arguments"), {}, result_fmtstr, result_context)
                return [effect], {}

            # add to the inventory report
            stock_levels[stock_code] = int(stock_level)

        # parsing was successful.
        result_fmtstr = _("Parsed Stock Levels: %(stock_levels)s.")
        result_context = { "stock_levels": repr(stock_levels) }

        effect = info(_("Parsed " + STOCK_LEVEL_OP_CODE + " Arguments"), {}, result_fmtstr, result_context)
        return [effect], { 'stock_levels': stock_levels }

class StockOut(OperationBase):
    """
    Parses stock codes and inventory levels from the provided message and sends
    the check and commit signals to the registered listeners.
    """

    def parse_arguments(self, arg_string, message):

        codes, remaining = gobbler.gobble(STOCK_CODE, arg_string)

        if len(remaining) > 0:
            # there are still characters remaining, meaning there was a parsing failure
            result_fmtstr = _("OK until: %(remaining_chars)s. " \
                                "Please fix and send again.")
            result_context = { "remaining_chars": remaining }

            effect = error(_("Error Parsing " + STOCK_OUT_OP_CODE + " Arguments"), {}, result_fmtstr, result_context)
            return [effect], {}

        if codes == None:
            # could not parse any useful information
            # there are still characters remaining, meaning there was a parsing failure
            result_fmtstr = _("No stock code found. " \
                                "Please fix and send again.")
            result_context = { "remaining_chars": remaining }

            effect = error(_("Error Parsing " + STOCK_OUT_OP_CODE + " Arguments"), {}, result_fmtstr, result_context)
            return [effect], {}

        # codes is a one element list containing the stock code
        stock_code = codes[0]

        # parsing was successful.
        result_fmtstr = _("Parsed Stock Out: %(stock_out_code)s.")
        result_context = { "stock_out_code": stock_code }

        effect = info(_("Parsed " + STOCK_OUT_OP_CODE + " Arguments"), {}, result_fmtstr, result_context)
        return [effect], { 'stock_out_code': stock_code }