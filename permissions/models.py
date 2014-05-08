from rapidsms.models import Contact
from django.db import models

class HierarchyNode(models.Model):    
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
    # The complete name of this facility
    name = models.CharField(max_length=250)
   
    #TODO: remove phone_number / address ?
    #TODO: add location?
    #TODO: add administrator?
    # The phone number for this facility
    phone_number = models.CharField(max_length=25, blank=True)

    # The address of this facility
    address = models.CharField(max_length=200, blank=True)

    # The position of this facility in the administrative hierarchy
    hierarchy_node = models.ForeignKey(HierarchyNode)
    
    class Meta:
        verbose_name_plural="facilities"
        ordering = ['name']

    def __unicode__(self):
        return self.name

class Role(models.Model):
    # The name of this role
    name = models.CharField(max_length=100)

    # A description of this role
    description = models.TextField(blank=True)

    # The opcodes for operations that this role is allowed to carry out
    op_codes = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class SimContact(Contact):
    # The role and permitted operations for this user
    role = models.ForeignKey(Role)

    # The facility where this user works
    facility = models.ForeignKey(Facility)
