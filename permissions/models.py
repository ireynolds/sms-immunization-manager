from rapidsms.models import Contact
from django.db import models

# Create your models here.

class HierarchyNode(models.Model):    
    # The parent of this entity in the hierarchy. If None, indicates a root node
    parent = models.ForeignKey('self', blank=True, null=True)

    # The name of the administrative level for the node in the hierarchy
    name = models.CharField(max_length=200)

    def __unicode__(self):
        if self.parent:
            return "level: %s (parent level: %s )" % (self.name, self.parent.name)
        else:
            return "root: %s" % self.name

class Facility(models.Model):
    # The complete name of this facility
    name = models.CharField(max_length=250)
   
    # TODO: make phone_number / address optional?
    # The phone number for this facility
    phone_number = models.CharField(max_length=25)

    # The address of this facility
    address = models.CharField(max_length=200)

    # The position of this facility in the administrative hierarchy
    hierarchy_node = models.ForeignKey(HierarchyNode)
    
    class Meta:
        verbose_name_plural="facilities"
        ordering = ['name']

    def __unicode__(self):
        return self.name

#   TODO: Location
#   TODO: Administrator

class Role(models.Model):
    # The name of this role
    name = models.CharField(max_length=100)

    # A description of this role
    description = models.TextField(blank=True)

    # The opcodes for operations that this role is allowed to carry out
    op_code = models.CharField(max_length=200)

class SimContact(Contact):
    # The role and permitted operations for this user
    role = models.ForeignKey(Role)

    # The facility where this user works
    facility = models.ForeignKey(Facility)
