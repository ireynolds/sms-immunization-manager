from django.db import models
from django.db.models import Q
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from rapidsms.models import Contact, Connection
from rapidsms.contrib.messagelog.models import Message
from moderation.models import MessageEffect, MODERATOR_PRIORITIES
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

        If a cycle exists in the hierarchy graph that contains this node, returns None.
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

    def moderation_contacts_count(self):
        """
        Returns the number of contacts in this administrative region that have undismissed message
        effects that require moderator action.
        """
        # TODO: Perhaps we should create a many-to-many ancestor relationship to accelerate this
        # computation, instead of having to traverse the tree in Python. For simplicity (and since
        # the administrative tree is relatively shallow) we do things the slow way for now.
        count = 0

        # Count moderations on facilities belonging to this node
        for facility in self.facility_set.all():
            count += facility.moderation_contacts().count()

        # Count the moderations of any child nodes
        # TODO: This will infinitely loop if a cycle exists. Fix this, or ensure cycles never exist.
        for node in self.children.all():
            count += node.moderation_contacts_count()

        return count


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

    def moderation_effects(self):
        """
        Returns a QuerySet of undismissed MessageEffects associated with this facility that require
        moderator action.
        """
        in_facility = Q(message__contact__contactprofile__facility=self)
        not_dismissed = Q(moderator_dismissed=False)
        moderator_priority = Q(priority__in=MODERATOR_PRIORITIES)
        return MessageEffect.objects.filter(in_facility & not_dismissed & moderator_priority)

    def moderation_contacts(self):
        """
        Returns a QuerySet of Contacts associated with this facility that have undismissed effects
        that require moderation action.
        """
        # Group by Contact id
        contact_pks = self.moderation_effects().values_list('message__contact', flat=True)

        # Create the Contact query. Note that this produces a SQL subquery, and does not evaluate
        # the Python value of the contact_pks QuerySet.
        return Contact.objects.filter(pk__in=contact_pks)

class ContactProfile(models.Model):
    """
    A user who interacts with the SMS immunization manager
    """
    # The rapidsms Contact that this ContactProfile maps to
    contact = models.OneToOneField(Contact, primary_key=True)

    # The facility where this user works
    facility = models.ForeignKey(Facility, blank=True, null=True)

    # The name of this role
    # TODO: For consistency this should just be 'role'
    role_name = models.CharField(max_length=100, 
                            choices=settings.ROLE_CHOICES, 
                            default=settings.DATA_REPORTER_ROLE)

    def __unicode__(self):
        return "%s (%s)" % (self.contact.name, self.get_role_name_display())

    def get_op_codes(self):
        """
        Returns the list of opcodes this user is allowed to use.
        """
        return dict(settings.ROLE_OP_CODES)[self.role_name]

    def get_phone_number(self):
        """
        Returns the phone number associated with this contact. If no phone number exists, returns
        None.
        """
        connections = Connection.objects.filter(contact=self.contact, 
            backend__name=settings.PHONE_BACKEND)
        if len(connections) == 0:
            return None
        return connections[0].identity


    def moderation_effects(self):
        """
        Returns a QuerySet of undismissed MessageEffects associated with this Contact that require
        moderator action.
        """
        in_contact = Q(message__contact__contactprofile=self)
        not_dismissed = Q(moderator_dismissed=False)
        moderator_priority = Q(priority__in=MODERATOR_PRIORITIES)
        return MessageEffect.objects.filter(in_contact & not_dismissed & moderator_priority)

    def moderation_messages(self):
        """
        Returns a QuerySet of Messages associated with this Contact that contain undismissed
        MessageEffects that require moderator action.
        """
        message_pks = self.moderation_effects().values_list('message', flat=True)
        # Note that this produces a SQL subquery, and does not evaluate the QuerySet message_pks
        return Message.objects.filter(pk__in=message_pks)


# Create a ContactProfile whenever a Contact is created
@receiver(post_save, sender=Contact)
def create_contact_profile_if_none_exists(sender, instance, **kwargs):
    if not ContactProfile.objects.filter(contact=instance).exists():
        profile = ContactProfile()
        profile.contact = instance
        profile.save()
            
# Register models for versioning
reversion.register(HierarchyNode)
reversion.register(Facility)
reversion.register(ContactProfile)
