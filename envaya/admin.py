from django.contrib import admin
from .models import SMS,Status

class SMSAdmin(admin.ModelAdmin):
	list_display = ['phone_number','network','now','power','battery','network','created','sender','message','timestamp']
	
	
class StatusAdmin(admin.ModelAdmin):
	list_display = ['phone_number','network','now','power','battery','network','created','phone_status']
	
admin.site.register(SMS,SMSAdmin)
admin.site.register(Status,StatusAdmin)