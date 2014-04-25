import logging
from sim.operations import commit_signal
from stock.apps import *
from equipment.apps import *

logger = logging.getLogger("rapidsms")

def fridge_failure_notification(message, **kwargs):
    """
    A notification stub
    """
    logger.debug("Fridge failure notification sent")
    message.respond("Fridge failure notification sent")

def stock_out_notification(message, **kwargs):
    """
    A notification stub
    """
    logger.debug("Stock out notification sent")
    message.respond("Stock out notification sent")


commit_signal.connect(fridge_failure_notification, sender=FridgeFailure)
commit_signal.connect(stock_out_notification, sender=StockOut)