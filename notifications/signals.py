import logging
from sim.operations import check_signal, commit_signal
from stock.apps import *
from equipment.apps import *

logger = logging.getLogger("rapidsms")

def equipment_failure_check(message, **kwargs):
    equipment_id = kwargs['equipment_id']
    if equipment_id not in [None, 'A', 'BC', 'D']:
        return "Message OK until %s. Unrecognized equipment code. Please fix and send again." % (equipment_id,)

def equipment_failure_commit(message, **kwargs):
    # TODO: Send notification
    logger.debug("Equipment failure notification sent")

def stock_out_notification(message, **kwargs):
    """
    A notification stub
    """
    logger.debug("Stock out notification sent")
    message.respond("Stock out notification sent")


#commit_signal.connect(fridge_failure_notification, sender=FridgeFailure)
#commit_signal.connect(stock_out_notification, sender=StockOut)