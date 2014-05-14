from utils.operations import OperationBase
from operation_parser.gobbler import Gobbler, LABEL
from moderation.models import error_parse, ok_parse
from django.utils.translation import ugettext_noop as _

class EquipmentBase(OperationBase):

    def _ok(self, opcode, args):
        return ok_parse(opcode, 
            "Parsed: equipment_id is %(equipment_id)s.", args)

    def _error_extra_chars(self, opcode, arg_string):
        return error_parse(opcode, arg_string, reason="Chars after equipment ID not allowed.")

    def _error_unrecognized_chars(self, opcode, arg_string):
        return error_parse(opcode, arg_string, reason="Should start with equipment ID.")

    def _error_no_equipment_id(self, opcode, arg_string):
        return error_parse(opcode, arg_string, reason="Must provide an equipment ID.")

    def parse_arguments(self, opcode, arg_string, message):
        args = {}
        effects = []
        
        g = Gobbler(arg_string.upper())

        equipment_id = g.gobble(LABEL)
        args['equipment_id'] = equipment_id

        if equipment_id:
            if g.remainder:
                args, effect = None, self._error_extra_chars(opcode, arg_string)
            else:
                args, effect = args, self._ok(opcode, args)
        else:
            if g.remainder:
                args, effect = None, self._error_unrecognized_chars(opcode, arg_string)
            else:
                args, effect = None, self._error_no_equipment_id(opcode, arg_string)
        effects.append(effect)

        return (effects, args)  

class EquipmentFailure(EquipmentBase):
    pass

class EquipmentRepaired(EquipmentBase):
    pass