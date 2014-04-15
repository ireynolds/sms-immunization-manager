from django.contrib import admin
from models import *
import reversion

class FacilityAdmin(reversion.VersionAdmin):
    pass

class PhoneUserAdmin(reversion.VersionAdmin):
    pass

class ActionInline(admin.TabularInline):
    model=MessageAction

class MessageAdmin(admin.ModelAdmin):
    inlines = [ActionInline]

class MessageActionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Facility, FacilityAdmin)
admin.site.register(PhoneUser, PhoneUserAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MessageAction, MessageActionAdmin)