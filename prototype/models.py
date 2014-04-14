from django.db import models
from django.core.urlresolvers import reverse

class HeirarchyNode(models.Model):
    """
    A node in the administrative heirarchy of a country
    """
    # The complete name of the administrative entity
    name = models.CharField(max_length=100)

    # A short abbreviation. Will typically be displayed in the context of parent nodes.
    abbreviation = models.CharField(max_length=10, blank=True)

    # A URL-suitable unique identifier for this entity
    slug = models.SlugField(max_length=50, unique=True)

    # A description of this entity, localized for residents of the entity
    description = models.TextField(blank=True)

    # The primary key of this administrative entity in DHIS2
    dhis2_pk = models.CharField(max_length=100)

    # The parent of this entity
    parent = models.ForeignKey("HeirarchyNode", blank=True, null=True, related_name="children")

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/prototype/node/%d/" % self.pk

    def moderations_count(self):
        """
        Returns the number of pending moderations in this region and its children
        """
        total = self.moderations().count()

        for node in self.children.all():
            total += node.moderations_count()

        return total

    def phone_users(self):
        """
        Returns the number of phone users in this region and its children
        """
        total = self.phoneuser_set.all().count()

        for node in self.children.all():
            total += node.phone_users()

        return total

    def children_count(self):
        """
        Returns the number of child nodes (including children of children, etc.)
        """
        total = 0
        for node in self.children.all():
            total += 1 + node.children_count()

        return total

    def root_path(self):
        """
        Returns a path from this node to a root node.
        """
        node = self
        path = []

        while node != None:
            path.append(node)
            node = node.parent

        path.reverse()
        return path

    def moderations(self):
        """
        Returns a collection of messages for this region that require moderation
        """
        return Message.objects.filter(user__heirarchy_node=self, moderation_hold=True, message_context=None)

class PhoneUser(models.Model):
    """
    A user that communicates via SMS messaging
    """
    # The phone number associated with this user
    number = models.CharField(max_length=25)

    # The name of this user
    name = models.CharField(max_length=100, blank=True)

    # The administrative entity for which this user works
    heirarchy_node = models.ForeignKey(HeirarchyNode, blank=True, null=True)

    # If True, this user was created automatically in response to an unexpected
    # message and has not yet been approved by a moderator
    moderation_hold = models.BooleanField(default=True)

    def __unicode__(self):
        if self.name:
            return "%s (%s)" % (self.number, self.name)
        else:
            return self.number

class Message(models.Model):
    """
    An SMS message that was received
    """
    # The phone number that sent this message
    number = models.CharField(max_length=25)

    # When the message was received
    date = models.DateTimeField(auto_now_add = True)

    # The contents of the message
    contents = models.TextField()

    # The user associated with this message
    user = models.ForeignKey(PhoneUser)

    # If True, this message could not be automatically processed and requires moderator action
    moderation_hold = models.BooleanField(default=True)

    # The message this message pertains to. Used when disambiguation or confirmation texts are
    # received
    message_context = models.ForeignKey("Message", related_name="context_children", blank=True, null=True)

    def __unicode__(self):
        return "%s: '%s'" % (self.number, self.contents)

    def get_absolute_url(self):
        if self.message_context == None:
            return "/prototype/message/%d/" % self.pk
        else:
            return self.message_context.get_absolute_url();

    def conversation(self):
        """
        Returns the sequence of message and actions taken to process this message. Returns a list
        of Message and MessageResult instances in chronological order from earliest to latest.
        """
        result = [self]
        result.extend(self.context_children.all())
        result.extend(self.results.all())
        result.sort(key=lambda x: x.date)
        return result

    def conversation_template(self):
        """
        Returns the name of a template used to render this item in a conversation
        """
        return "include/conversation/message.html"

ACTIONS = (
    ('SYNTAX', 'Malformed Message'),
    ('DHIS2', 'DHIS2 Update Made'),
    ('DISAMBIG', 'User Data Disambiguated'),
    ('DUPLICATE', 'Duplicate Update Detected'),
    ('RESPONSE', 'SMS Response Sent'),
    ('MODERATION', 'Approved by Moderator'),
)

class MessageResult(models.Model):
    """
    An action that was taken as a result of a message
    """
    # The action that was taken
    action = models.CharField(max_length=15, choices=ACTIONS)

    # A description of the action that was taken
    description = models.TextField(blank=True)

    # The message for which the action is taken
    message = models.ForeignKey(Message, related_name="results")

    # When the action was taken
    date = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return "%s: %s" % (self.action, self.description)

    def conversation_template(self):
        """
        Returns the name of a template used to render this item in a conversation
        """
        return "include/conversation/result.html"

    def display_action(self):
        """
        Returns the human-readable action of this MessageResult
        """
        return dict(ACTIONS)[self.action]