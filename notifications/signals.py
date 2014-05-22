import logging
from utils.operations import semantic_signal, commit_signal
from stock.apps import *
from equipment.apps import *
from django.dispatch.dispatcher import receiver
from moderation.models import *
from django.utils.translation import ugettext_noop as _

STUBBED_EQUIPMENT_IDS = ['A', 'B', 'C']

##
## Equipment Failure
##

@receiver(semantic_signal, sender=EquipmentFailure)
def equipment_failure_check(message, **kwargs):
    equipment_id = kwargs['equipment_id']
    
    if equipment_id not in STUBBED_EQUIPMENT_IDS:
        effect = error(
            _("Error Interpreting %(op_code)s Arguments"), { 'op_code': kwargs['opcode'] },
            _("Unrecognized equipment label %(equipment_id)s."), { 'equipment_id': equipment_id }
        )
    else:
        effect = info(
            _("Parsed %(op_code)s Arguments"), { 'op_code': kwargs['opcode'] },
            _("Equipment label: %(equipment_id)s"), { 'equipment_id': equipment_id }
        )

    return [effect]



@receiver(commit_signal, sender=EquipmentFailure)
def equipment_failure_commit(message, **kwargs):
    # TODO Implement
    return []

##
## Equipment Repaired
##

@receiver(semantic_signal, sender=EquipmentRepaired)
def equipment_repaired_check(message, **kwargs):
    equipment_id = kwargs['equipment_id']
    
    if equipment_id not in STUBBED_EQUIPMENT_IDS:
        effect = error(
            _("Error Interpreting %(op_code)s Arguments"), { 'op_code': kwargs['opcode'] },
            _("Unrecognized equipment label %(equipment_id)s."), { 'equipment_id': equipment_id }
        )
    else:
        effect = info(
            _("Parsed %(op_code)s Arguments"), { 'op_code': kwargs['opcode'] },
            _("Equipment label: %(equipment_id)s"), { 'equipment_id': equipment_id }
        )

    return [effect]

@receiver(commit_signal, sender=EquipmentRepaired)
def equipment_repaired_commit(message, **kwargs):
    # TODO Implement
    return []

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