#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

############################################################
#
# NOTE:
# This code was copied directly from the RapidSMS source
# code to provide one small modification.
#
# The parse phase method was changed to be filter so that the
# logger_msg would be attached to the message earlier.
#
############################################################


from django.utils import timezone
from rapidsms.apps.base import AppBase
from .models import Message


class MessageLogApp(AppBase):

    def _log(self, direction, msg):
        if not msg.contact and not msg.connection:
            raise ValueError
        text = msg.raw_text if direction == Message.INCOMING else msg.text
        return Message.objects.create(
            date=timezone.now(),
            direction=direction,
            text=text,
            contact=msg.contact,
            connection=msg.connection,
        )

    def filter(self, msg):
        # annotate the message as we log them in case any other apps
        # want a handle to them
        msg.logger_msg = self._log(Message.INCOMING, msg)

    def outgoing(self, msg):
        msg.logger_msg = self._log(Message.OUTGOING, msg)
