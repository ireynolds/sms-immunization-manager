from django.contrib import admin
from rapidsms.models import Contact
from rapidsms.admin import ContactAdmin
from user_registration.models import *

class HierarchyNodeAdmin(admin.ModelAdmin):
    pass

class FacilityAdmin(admin.ModelAdmin):
    pass

class ContactProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(HierarchyNode, HierarchyNodeAdmin)
admin.site.register(Facility, FacilityAdmin)
admin.site.register(ContactProfile, ContactProfileAdmin)

# Add an inline contact profile form to the Contact form
class ContactProfileInline(admin.StackedInline):
    model = ContactProfile
    can_delete = False

class UpdatedContactAdmin(ContactAdmin):
    inlines = tuple(list(ContactAdmin.inlines) + [ContactProfileInline])

admin.site.unregister(Contact)
admin.site.register(Contact, UpdatedContactAdmin)