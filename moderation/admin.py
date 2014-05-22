from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from moderation.models import *

class MessageEffectAdmin(admin.ModelAdmin):
    pass

admin.site.register(MessageEffect, MessageEffectAdmin)

# Add a moderator profile form to the existing User form
class ModeratorProfileInline(admin.StackedInline):
    model = ModeratorProfile
    can_delete = False

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (ModeratorProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)