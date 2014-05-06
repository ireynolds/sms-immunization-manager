import logging
from sim.operations import check_signal, commit_signal
from stock.apps import *
from equipment.apps import *

logger = logging.getLogger("rapidsms")

stubbed_equipment_ids = [None, 'A', 'BC', 'D']

##
## Equipment Failure
##

def equipment_failure_check(message, **kwargs):
    equipment_id = kwargs['equipment_id']
    if equipment_id not in stubbed_equipment_ids:
        return "Message OK until %s. Unrecognized equipment code. Please fix and send again." % (equipment_id,)
check_signal.connect(equipment_failure_check, sender=EquipmentFailure)

def equipment_failure_commit(message, **kwargs):
    # TODO: Send notification
    logger.debug("Equipment failure notification sent")
commit_signal.connect(equipment_failure_commit, sender=EquipmentFailure)

##
## Equipment Repaired
##

def equipment_repaired_check(message, **kwargs):
    equipment_id = kwargs['equipment_id']
    if equipment_id not in stubbed_equipment_ids:
        return "Message OK until %s. Unrecognized equipment code. Please fix and send again." % (equipment_id,)
check_signal.connect(equipment_repaired_check, sender=EquipmentRepaired)

def equipment_repaired_commit(message, **kwargs):
    pass
commit_signal.connect(equipment_repaired_commit, sender=EquipmentRepaired)

##
## Stock Out
##

def stock_out_notification(message, **kwargs):
    """
    A notification stub
    """
    logger.debug("Stock out notification sent")
    message.respond("Stock out notification sent")
#commit_signal.connect(stock_out_notification, sender=StockOut)