from django.db import models
from django.core.urlresolvers import reverse
import reversion

class Facility(models.Model):
    """
    A facility represented in DHIS2
    """
    # The primary key of this facility in DHIS2
    dhis2_pk = models.CharField(max_length=100)

    # The complete name of this facility
    name = models.CharField(max_length=250)

    # A description of this facility, localized for workers at this facility
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural="facilities"
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/prototype/facility/%d/' % self.pk

    def pending_actions(self):
        return MessageAction.objects.filter(moderation_state='PENDING', message__user__facility=self)

class PhoneUser(models.Model):
    """
    A user that communicates via SMS messaging
    """
    # The phone number associated with this user
    number = models.CharField(max_length=25)

    # The name of this user
    name = models.CharField(max_length=100, blank=True)

    # The administrative entity for which this user works
    facility = models.ForeignKey(Facility, blank=True, null=True)

    def __unicode__(self):
        if self.name:
            return "%s (%s)" % (self.name, self.number)
        else:
            return self.number

    def pending_actions(self):
        return MessageAction.objects.filter(moderation_state='PENDING', message__user=self)

    def get_absolute_url(self):
        return '/prototype/user/%d/' % self.pk

    def log_items(self):
        items = []
        items.extend([(m, m.date) for m in self.message_set.all()])

        versions = [(v.field_dict, v.revision.date_created) for v in reversion.get_for_object(self)]

        # A bit of a hack: add a RENDER_TEMPLATE for each version dictionary to make it consistent
        # with other models used in the conversation view
        for fields, date in versions:
            fields['RENDER_TEMPLATE'] = "include/conversation/user_version.html"
            fields[date] = date
            items.append((fields, date))

        items.sort(key=lambda i: i[1])

        return map(lambda i: i[0], items)



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

    RENDER_TEMPLATE = "include/conversation/message.html"

    class Meta:
        get_latest_by = 'date'

    def __unicode__(self):
        return "%s: '%s'" % (self.number, self.contents)

    def get_absolute_url(self):
        return "/prototype/message/%d/" % self.pk

MODERATION_STATES = (
    ('NONE', "No moderation required"),
    ('PENDING', "Pending moderation"),
    ('APPROVED', "Approved"),
    ('DISMISSED', 'Dismissed'),
)

ACTION_TITLES = (
    ('MALFORMED', 'Malformed Message'),
    ('DHIS2_UPDATE', 'DHIS2 Update'),
    ('USER_UPDATE', 'User Data Update'),
    ('SMS_RESPONSE', 'SMS Response'),
)

ACTION_ICONS = (
    ('MALFORMED', 'warning-sign'),
    ('DHIS2_UPDATE', 'cloud-upload'),
    ('USER_UPDATE', 'pencil'),
    ('SMS_RESPONSE', 'repeat'),
)

class MessageAction(models.Model):
    """
    An action that was taken as a result of a message. Can be held for moderation before being
    applied.
    """
    # The action that was taken
    action = models.CharField(max_length=15, choices=ACTION_TITLES)

    # A description of the action that was taken
    description = models.TextField(blank=True)

    # The message for which the action is taken
    message = models.ForeignKey(Message, related_name="actions")

    # When the action was created
    date = models.DateTimeField(auto_now_add = True)

    # The moderation state of this action
    moderation_state = models.CharField(max_length=15, choices=MODERATION_STATES)

    class Meta:
        get_latest_by = 'date'

    def __unicode__(self):
        return "%s: %s" % (self.action, self.description)

    def title(self):
        """
        Returns the human-readable title of this action
        """
        return dict(ACTION_TITLES)[self.action]

    def icon(self):
        """
        Returns the icon for this action
        """
        return dict(ACTION_ICONS)[self.action]

    def moderation_state_text(self):
        """
        Returns the human-readable moderation state of this action
        """
        return dict(MODERATION_STATES)[self.moderation_state]

    def get_absolute_url(self):
        return self.message.get_absolute_url()

# Register models for versioning
reversion.register(PhoneUser)
reversion.register(Facility)