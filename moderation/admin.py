from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from rapidsms.contrib.messagelog.admin import MessageAdmin
from rapidsms.contrib.messagelog.models import Message
from moderation.models import *

class MessageEffectAdmin(admin.ModelAdmin):
    pass

admin.site.register(MessageEffect, MessageEffectAdmin)

# Add a message effect inline form to the existing Message form
class MessageEffectInline(admin.StackedInline):
    model = MessageEffect
    can_delete = False
    extra = 1

class MessageAdmin(MessageAdmin):
    inlines = (MessageEffectInline,)

admin.site.unregister(Message)
admin.site.register(Message, MessageAdmin)

# Add a moderator profile form to the existing User form
class ModeratorProfileInline(admin.StackedInline):
    model = ModeratorProfile
    can_delete = False

class UserAdmin(UserAdmin):
    inlines = (ModeratorProfileInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)