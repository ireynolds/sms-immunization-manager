from utils.operations import semantic_signal
from stock.apps import *
from django.utils.translation import ugettext_noop as _
from moderation.models import *

def requires_even_phone_number(message, **kwargs):
    """
    A mock check signal receiver, which only allows messages from even phone numbers to proceed.
    """
    name = _("Valid Phone Number Check")
    n = int(message.connection.identity)
    if n % 2 != 0:
        return failure(name, {}, _("The number %(n)d is not even"), {"n":n})
    return success(name, {}, _("The number %(n)d is even"), {"n":n})

semantic_signal.connect(requires_even_phone_number, sender=StockLevel)
semantic_signal.connect(requires_even_phone_number, sender=StockOut)