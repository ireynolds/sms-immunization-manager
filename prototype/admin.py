from django.contrib import admin
from models import *

class HeirarchyNodeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

class PhoneUserAdmin(admin.ModelAdmin):
    pass

class MessageAdmin(admin.ModelAdmin):
    pass

class MessageResultAdmin(admin.ModelAdmin):
    pass

admin.site.register(HeirarchyNode, HeirarchyNodeAdmin)
admin.site.register(PhoneUser, PhoneUserAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MessageResult, MessageResultAdmin)