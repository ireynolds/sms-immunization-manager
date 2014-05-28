from utils.operations import semantic_signal
from stock.apps import *
from django.utils.translation import ugettext_noop as _
from moderation.models import *
from user_registration.models import *
from django.conf import settings

@receiver(semantic_signal)
def opcode_permissions_check(message, opcode, **kwargs):
    """
    A signal receiver to check that the user is permitted
    to perform the specified operation
    """

    contact_profile = message.connections[0].contact.contactprofile
    permitted_opcodes = contact_profile.get_op_codes()
    fmt_args = { 'requested_opcode' : opcode, 
                 'role' : contact_profile.get_role_description() }
    
    if opcode in permitted_opcodes:
    # TODO: check facility code
        effect = info(
                _("Operation allowed"), {},
                _("%(role)s requested to perform permitted operation %(requested_opcode)s."), fmt_args 
                )
    else:
        effect = error(
                _("Operation not permitted for this user"), {},
                _("%(role)s is not allowed to perform operation %(requested_opcode)s."), fmt_args
                )

    
    return [effect]

