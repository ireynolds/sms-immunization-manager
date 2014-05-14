from django.conf import settings
from rapidsms.models import Contact
from django.db import models
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


class SimContact(Contact):
    """
    A user who interacts with the SMS immunization manager
    """
    # The facility where this user works
    facility = models.ForeignKey(Facility)

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

    def save(self, *args, **kwargs):
        # ensures that opcodes match assigned role
        self.op_codes = self.role_name
        super(SimContact, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.get_role_name_display())
 

# Register models for versioning
reversion.register(HierarchyNode)
reversion.register(Facility)
reversion.register(SimContact)
