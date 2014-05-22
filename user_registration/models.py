from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from rapidsms.models import Contact
import reversion

class HierarchyNode(models.Model):    
    """
    A HierarchyNode represents a level in the administration hierarchy
    for a country's cold chain. If a HierarchyNode has no parents, it
    signifies a root node representing the top level of the hierarchy.
    """
    # The parent of this entity in the hierarchy. If blank, indicates a root node
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')

    # The name of the administrative level for the node in the hierarchy
    name = models.CharField(max_length=200)

    def __unicode__(self):
        if self.parent:
            return "%s (parent is %s )" % (self.name, self.parent.name)
        else:
            return "%s is root" % self.name

class Facility(models.Model):
    """
    A facility represented in DHIS2
    """
    # The complete name of this facility
    name = models.CharField(max_length=250)
   
    # A description of this facitliy, perhaps including information about
    # phone number, address, administrator, etc.
    description = models.TextField(max_length=200, blank=True)

    # The position of this facility in the administrative hierarchy
    hierarchy_node = models.ForeignKey(HierarchyNode)
    
    class Meta:
        verbose_name_plural="facilities"
        ordering = ['name']

    def __unicode__(self):
        return self.name

class UserProfile(models.Model):
    """
    A user who interacts with the SMS immunization manager
    """
    # The rapidsms Contact that this UserProfile maps to
    contact = models.OneToOneField(Contact, primary_key=True)

    # The facility where this user works
    facility = models.ForeignKey(Facility, blank=True, null=True)

    # The name of this role
    role_name = models.CharField(max_length=100, 
                            choices=settings.ROLE_CHOICES, 
                            default=settings.DATA_REPORTER_ROLE)

    # A description of this role
    role_description = models.TextField(blank=True)

    # The opcodes for operations that this role is allowed to carry out
    op_codes = models.CharField(max_length=100, 
                                choices=settings.ROLE_OP_CHOICES, 
                                default=settings.DATA_REPORTER_ROLE)

    # TODO: Remove?
    def save(self, *args, **kwargs):
        # ensures that opcodes match assigned role
        self.op_codes = self.role_name
        super(UserProfile, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s (%s)" % (self.contact.name, self.get_role_name_display())

# Create a UserProfile whenever a Contact is created
@receiver(post_save, sender=Contact)
def my_handler(sender, instance, **kwargs):
    if not UserProfile.objects.filter(contact=instance).exists():
        profile = UserProfile()
        profile.contact = instance
        profile.save()
            
# Register models for versioning
reversion.register(HierarchyNode)
reversion.register(Facility)
reversion.register(UserProfile)
