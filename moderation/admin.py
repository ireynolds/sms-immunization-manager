from django.contrib import admin
from moderation.models import *

class MessageEffectAdmin(admin.ModelAdmin):
    pass

admin.site.register(MessageEffect, MessageEffectAdmin)