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
    effect = notify(
        _("Equipment Failure!"), {},
        _("Equipment label: %(equipment_id)s"), {'equipment_id' : kwargs['equipment_id']}
    )
    return [effect]

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
    effect = notify(
        _("Equipment Repaired"), {},
        _("Equipment label: %(equipment_id)s"), {'equipment_id' : kwargs['equipment_id']}
    )
    return [effect]

##
## Stock Out
##

@receiver(commit_signal, sender=StockOut)
def stock_out_notification(message, **kwargs):
    effect = notify(
        _("Stock Out"), {},
        _("Vaccine %(stock_out)s is out of stock"), {'stock_out' : kwargs['stock_out']}
    )

    return [effect]
