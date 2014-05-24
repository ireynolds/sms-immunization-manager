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
        return self.name

    def root_path(self):
        """
        Returns a path from this node to a root node. The first element in the returned list is
        this node. The last element in the returned list is an ancestor of this node which has no
        parent. If this node is a root node, returns [self].

        If a cycle exists in the hierarchy graph which contains this node, returns None.
        """
        path = []
        current_node = self

        while current_node != None:
            if current_node in path:
                # A cycle was detected
                # TODO: Should an exception be thrown instead?
                return None
            path.append(current_node)
            current_node = current_node.parent
            
        return path



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

    @classmethod
    def from_code(cls, code):
        '''
        Returns the facility with the given facility code, or raises an
        error if no such facility exists.
        ''' 
        # TODO: Implement
        return None

class ContactProfile(models.Model):
    """
    A user who interacts with the SMS immunization manager
    """
    # The rapidsms Contact that this ContactProfile maps to
    contact = models.OneToOneField(Contact, primary_key=True)

    # The facility where this user works
    facility = models.ForeignKey(Facility, blank=True, null=True)

    # The name of this role
    role_name = models.CharField(max_length=100, 
                            choices=settings.ROLE_CHOICES, 
                            default=settings.DATA_REPORTER_ROLE)

    def __unicode__(self):
        return "%s (%s)" % (self.contact.name, self.get_role_description())

    def get_role_description(self):
        """
        Returns a description of this user's role, as a lazily internationalized string.
        """
        return dict(settings.ROLE_CHOICES)[self.role_name]

    def get_op_codes(self):
        """
        Returns the list of opcodes this user is allowed to use.
        """
        return dict(settings.ROLE_OP_CODES)[self.role_name]


# Create a ContactProfile whenever a Contact is created
@receiver(post_save, sender=Contact)
def create_user_profile_if_none_exists(sender, instance, **kwargs):
    if not ContactProfile.objects.filter(contact=instance).exists():
        profile = ContactProfile()
        profile.contact = instance
        profile.save()
            
# Register models for versioning
reversion.register(HierarchyNode)
reversion.register(Facility)
reversion.register(ContactProfile)
