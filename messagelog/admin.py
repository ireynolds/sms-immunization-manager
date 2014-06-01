#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

############################################################
#
# NOTE:
# This code was copied directly from the RapidSMS source
# code to provide one small modification.
#
# The line that registers Message has been commented out
# because it has already been registered.
#
############################################################


from django.contrib import admin
from .models import Message


class MessageAdmin(admin.ModelAdmin):
    list_display = ("text", "direction", "who", "date")
    list_filter = ("direction", "date")





#admin.site.register(Message, MessageAdmin)
