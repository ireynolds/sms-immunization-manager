from rapidsms.models import Connection
from rapidsms.apps.base import AppBase
from messagelog import *
from moderation.models import * #urgent, info, complete_effect, FILTER
from django.utils.translation import ugettext_noop as _

class SpamFilter(AppBase):
    def filter(self, msg):
        """Filter out messages from unrecognized users"""
        if msg.connections[0].contact is None:
            effect = error(
                    _("Received message from unrecognized user"), {},
                    _("%(phone_number)s is an unrecognized user"), { 'phone_number' : msg.connections[0].identity }
                    )
            complete_effect(effect, msg.logger_msg, FILTER)

            # If message is spam, halt further processing of message
            return True
        else:
            effect = info(
                    _("Received message from recognized user"), {},
                    _("%(phone_number)s is a recognized user"), { 'phone_number' : msg.connections[0].identity }
                    )
            complete_effect(effect, msg.logger_msg, FILTER)
            return False
