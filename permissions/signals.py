from sim.operations import check_signal
from stock.apps import *

def requires_even_phone_number(message, **kwargs):
    """
    A mock check signal receiver, which only allows messages from even phone numbers to proceed.
    """

    if int(message.connection.identity) % 2 == 0:
        return None
    return "Odd numbered phone numbers are not allowed!"

# check_signal.connect(requires_even_phone_number, sender=StockLevel)
check_signal.connect(requires_even_phone_number, sender=StockOut)