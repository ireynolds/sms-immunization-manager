import django.dispatch
from sim.operations import OperationBase, filter_by_opcode

class StockLevel(OperationBase):
    """
    Parses stock codes and inventory levels from the provided message and sends
    the check and commit signals.
    """

    @filter_by_opcode
    def handle(self, message):

        # parse all stock codes and value pairs
        parsed = parse_stock_levels(get_stock_codes, message.text)
        stock_levels = parsed(0)
        remaining = parsed(1)

        if len(remaining) > 0:
            # there was a parsing failure
            message.respond("StockLevel parse failed! Successfully parsed everything before: %s" % remaining)
            return None

        check_results, commit_results = self.send_signals(message=message,
                                                          stock_levels=stock_levels)

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

# temp location - this information will not be stored here.
def get_stock_codes():
    return ["A", "B", "C", "D", "AA", "BB", "CD"]


def get_stock_codes_regex(stock_codes):
    """
    Produces a regex OR of all the provided stock codes
    stock_codes: a list of stock code strings
    returns: a regex string
    """

    regex = "("
    for code in stock_codes:
        regex += "|" + code
    regex += ")"
    return regex

def parse_stock_levels(stock_codes, message):
    re_codes = get_stock_codes_regex(stock_codes)
    stock_levels = map()

    # try to parse first stock code
    parsed = gobble(re_codes, message)

    if parsed:
        stock_code = parsed(0)
        parsed = gobble("\d+", parsed(1))
        if parsed:
            stock_inv = parsed(0)
            stock_levels[stock_code] = int(stock_inv)

    # try to parse the remaining stock codes
    while parsed:
        parsed = gobble(re_codes, parsed(1))
        if parsed:
            stock_code = parsed(0)
            parsed = gobble("\d+", parsed(1))
            if parsed:
                stock_inv = parsed(0)
                stock_levels[stock_code] = int(stock_inv)

    return (stock_levels, parsed)

def gobble(pattern, source):
    matched = re.match("\\W*" + pattern, source)

    if (matched):
        matched = matched.group(0)
        return (matched, source[len(matched):])

    return None
