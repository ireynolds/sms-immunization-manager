import django.dispatch
from utils.operations import OperationBase
from operation_parser import gobbler
from moderation.models import *
from django.utils.translation import ugettext_noop as _

# Regular Expressions for parsing the stock code and level
STOCK_CODE = "[A-z]+"
STOCK_LEVEL = "[0-9]+"
NOT_ALPHA_NUM = "[^A-z0-9]*"

class StockBase(OperationBase):
    def _error_unrecognized_chars(self, opcode):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments containing unrecognized characters in the argument string.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Extra characters found in message."), {}
        )

class StockLevel(StockBase):
    """Implements the StockLevel SMS API."""

    helptext = "For example, %(opcode)s P 2100 M 10. Reports 2100 doses of vaccine P, 10 of M, and 0 of any others."

    def _error_none_found(self, opcode):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments containing no recognized stock levels.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("No stock levels found."), {}
        )

    def _error_duplicate_stock_levels(self, opcode):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments containing duplicate stock levels.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Found a duplicate stock code."), {}
        )

    def _ok(self, opcode, args):
        '''Return a MessageEffect that indicates success.'''
        return info(
            _("Parsed %(op_code)s Arguments"), { 'op_code': opcode },
            _("Parsed: stock_levels is %(stock_levels)s."), args
        )

    def parse_arguments(self, opcode, arg_string, message):
        """
        Parses stock codes and inventory levels from the provided argument
        string. Expects one or more of the format:
            <Stock Code> <Inventory Level>

        Returns a 2-tuple containing a list of MessageEffects representing the
        results of the parsing, and a Python dictionary mapping 'stock_levels'
        to another dictionary which maps the parsed stock code strings to
        integer inventory levels.
        """
        levels, remaining = gobbler.gobble_all(STOCK_CODE + NOT_ALPHA_NUM + STOCK_LEVEL, arg_string)

        if len(remaining) > 0:
            # there are still characters remaining, meaning there was a parsing failure
            effect = self._error_unrecognized_chars(opcode)
            return [effect], {}

        if levels == None:
            # did not find any stock code and level combos
            effect = _error_none_found(opcode)
            return [effect], {}

        # create a dictionary: stock code -> stock level
        levels = [ gobbler.gobble(STOCK_CODE, l) for l in levels ]
        stock_levels = {}

        for stock_code, stock_level in levels:
            if stock_code in stock_levels:
                # there was a duplicate stock code in the message
                effect = self._error_duplicate_stock_levels(opcode)
                return [effect], {}

            # add to the inventory report
            stock_levels[stock_code] = int(stock_level)

        # parsing was successful.
        parsed_args = { 'stock_levels': stock_levels }
        effect = self._ok(opcode, parsed_args)
        return [effect], parsed_args

class StockOut(StockBase):
    """Implements the StockOut SMS API."""

    helptext = "For example, %(opcode)s P. In an emergency, reports that you are out of doses of vaccine P."

    def _ok(self, opcode, args):
        '''Return a MessageEffect that indicates success.'''
        return info(
            _("Parsed %(op_code)s Arguments"), { 'op_code': opcode },
            _("Parsed: stock_out is %(stock_out)s."), args
        )

    def _error_none_found(self, opcode):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments containing no recognized stock levels.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("No stock code found."), {}
        )

    def parse_arguments(self, opcode, arg_string, message):
        """
        Parses a single stock code from the provided argument string.
        Returns a 2-tuple containing a list of MessageEffects representing the
        results of the parsing, and a Python dictionary mapping 'stock_out'
        to the actual stock code found by the parsing.
        """

        codes, remaining = gobbler.gobble(STOCK_CODE, arg_string)

        if len(remaining) > 0:
            # there are still characters remaining, meaning there was a parsing failure
            effect = self._error_unrecognized_chars(opcode)
            return [effect], {}

        if codes == None:
            # could not parse any useful information
            effect = self._error_none_found(opcode)
            return [effect], {}

        # codes is a one element list containing the stock code
        stock_code = codes[0]

        # parsing was successful.
        parsed_args = { 'stock_out': stock_code }
        effect = self._ok(opcode, parsed_args)
        return [effect], parsed_args