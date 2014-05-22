from django.contrib import admin
from user_registration.models import *

class HierarchyNodeAdmin(admin.ModelAdmin):
    pass

class FacilityAdmin(admin.ModelAdmin):
    pass

class UserProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(HierarchyNode, HierarchyNodeAdmin)
admin.site.register(Facility, FacilityAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
