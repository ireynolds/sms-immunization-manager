import logging
from sim.operations import semantic_signal, commit_signal
from stock.apps import *
from equipment.apps import *
from django.dispatch.dispatcher import receiver

logger = logging.getLogger("rapidsms")

stubbed_equipment_ids = [None, 'A', 'BC', 'D']

##
## Equipment Failure
##

@receiver(semantic_signal, sender=EquipmentFailure)
def equipment_failure_check(message, **kwargs):
    equipment_id = kwargs['equipment_id']
    if equipment_id not in stubbed_equipment_ids:
        return "Message OK until %s. Unrecognized equipment code. Please fix and send again." % (equipment_id,)

@receiver(commit_signal, sender=EquipmentFailure)
def equipment_failure_commit(message, **kwargs):
    # TODO: Send notification
    logger.debug("Equipment failure notification sent")

##
## Equipment Repaired
##

@receiver(semantic_signal, sender=EquipmentRepaired)
def equipment_repaired_check(message, **kwargs):
    equipment_id = kwargs['equipment_id']
    if equipment_id not in stubbed_equipment_ids:
        return "Message OK until %s. Unrecognized equipment code. Please fix and send again." % (equipment_id,)

@receiver(commit_signal, sender=EquipmentRepaired)
def equipment_repaired_commit(message, **kwargs):
    pass

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