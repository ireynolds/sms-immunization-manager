import json
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy
from django.utils.encoding import force_text
from django.utils.functional import lazy
from django.utils import six

def create_effect(priority, noop_i18n_name, name_context, noop_i18n_desc, desc_context):
    """
    Returns an un-saved MessageEffect with the given success state, name and description.
    noop_i18n_name contains the name of this effect as a format string returned from a noop i18n
    function. name_context is a dictionary mapping replacement items in noop_i18n_name to their
    values. The corresponding desc fields represent a message describing the outcome of this event.

    Every check or commit signal listener must return a MessageEffect instance created using this
    function or its shortcut functions below.
    """
    instance = MessageEffect()
    instance.priority = priority
    instance.set_name(noop_i18n_name, name_context)
    instance.set_desc(noop_i18n_desc, desc_context)
    return instance

def debug(noop_i18n_name, name_context, noop_i18n_desc, desc_context):
    """
    Returns an un-saved MessageEffect with a debug priority. See create_effect for a description
    of this function's parameters.

    Debug effects are developer information of no relevance to users.
    """
    return create_effect(DEBUG, noop_i18n_name, name_context, noop_i18n_desc, desc_context)

def info(noop_i18n_name, name_context, noop_i18n_desc, desc_context):
    """
    Returns an un-saved MessageEffect with an info priority. See create_effect for a description
    of this function's parameters.

    Info effects document successes or other non-errors.
    """
    return create_effect(INFO, noop_i18n_name, name_context, noop_i18n_desc, desc_context)

def warn(noop_i18n_name, name_context, noop_i18n_desc, desc_context):
    """
    Returns an un-saved MessageEffect with a warning priority. See create_effect for a description
    of this function's parameters.

    Warning effects documents minor or non-user-actionable errors. Warnings typically are not
    returned to users, and do not prevent later processing from taking place.
    """
    return create_effect(WARN, noop_i18n_name, name_context, noop_i18n_desc, desc_context)

def error(noop_i18n_name, name_context, noop_i18n_desc, desc_context):
    """
    Returns an un-saved MessageEffect with an error priority. See create_effect for a description
    of this function's parameters.

    Error effects document user-actionable errors. Their messages may be returned to users and
    prevent later processing from taking place.
    """
    return create_effect(ERROR, noop_i18n_name, name_context, noop_i18n_desc, desc_context)

def urgent(noop_i18n_name, name_context, noop_i18n_desc, desc_context):
    """
    Returns an un-saved MessageEffect with an urgent priority. See create_effect for a description
    of this function's parameters.

    Urgent effects are critically important information that must be seen and acted upon
    immediately. Their messages are always returned to users and do not halt further message
    processing. Use sparingly, if ever.
    """
    return create_effect(URGENT, noop_i18n_name, name_context, noop_i18n_desc, desc_context)

def complete_effect(effect, message, stage, operation_index = None, opcode = ''):
    """
    Adds any remaining fields to effect not assigned by create_effect or its shortcut functions, and
    saves the given effect model. Used by receivers of MessageEffects created with create_effect
    or one of its shortcut functions above (e.g. a commit signal sender). Returns effect.

    The message parameter is an instance of messagelog.Message, which can typically be accessed
    via the msg.logger_msg field created by the messagelog app.
    """
    effect.message = message
    effect.stage = stage
    effect.operation_index = operation_index
    effect.opcode = opcode
    effect.save()
    return effect

# Define priority levels for message effects.
DEBUG = 'DEBUG'
INFO = 'INFO'
WARN = 'WARN'
ERROR = 'ERROR'
URGENT = 'URGENT'

PRIORITY_CHOICES = (
    (DEBUG, ugettext_lazy("Debug")),
    (INFO, ugettext_lazy("Debug")),
    (WARN, ugettext_lazy("Warning")),
    (ERROR, ugettext_lazy("Error")),
    (URGENT, ugettext_lazy("Urgent")),
)

# Define the stage an effect can occur in.
SYNTAX = 'SYNTAX'
SEMANTIC = 'SEMANTIC'
COMMIT = 'COMMIT'

STAGE_CHOICES = (
    (SYNTAX, ugettext_lazy("Syntax")),
    (SEMANTIC, ugettext_lazy('Semantic')),
    (COMMIT, ugettext_lazy('Commit')),
)

class MessageEffect(models.Model):
    """
    Logs the effects of each check and commit signal receiver for a message. This model is created
    by operation signal listeners to report their outcome to the signal sender, as well as log the
    outcome for moderation purposes. Some fields are stored as format strings and contexts to allow
    for later internationalization.
    """
    # The date and time when this effect was completed.
    date = models.DateTimeField(auto_now_add=True)

    # The RapidSMS message that signaled this effect
    message = models.ForeignKey("messagelog.Message")

    # The stage in which this effect occurred
    stage = models.CharField(max_length=10, choices=STAGE_CHOICES)

    # The priority of this effect's outcome
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)

    # The 0-indexed position of this operation in the message, if applicable
    operation_index = models.PositiveIntegerField(blank=True, null=True)

    # The opcode of this operation, if applicable
    opcode = models.CharField(max_length=2, blank=True)

    # If True, this effect has been reviewed and dismissed by a moderator
    moderator_dismissed = models.BooleanField(default="False")

    # The name of this effect, as an untranslated format string
    name_format = models.TextField()
    # The context used to render name_format as a JSON-encoded dictionary
    name_context = models.TextField()

    # A description of this effect's outcome, as an untranslated format string
    desc_format = models.TextField()
    # The context used to render desc_format
    desc_context = models.TextField()

    def __unicode__(self):
        context = {"name": unicode(self.get_name()), "desc": unicode(self.get_desc())}
        return ugettext(self.priority) + ugettext(" :: %(name)s: %(desc)s") % context

    def _set_lazy_i18n(self, format_field, context_field, format, context):
        """
        Helper function for setting lazy i18n fields
        """
        # Ensure that every replacement string in format is a key in context
        format % context

        setattr(self, format_field, unicode(format))
        setattr(self, context_field, json.dumps(context))

    def _get_lazy_i18n(self, format_field, context_field):
        """
        Helper function for getting lazy i18n fields
        """
        # Define a lazy function for evaluating a string format (i.e. f % d)
        lazy_format_string = lazy(lambda f, d: force_text(f) % d, six.text_type)

        format = ugettext_lazy(getattr(self, format_field))
        context = json.loads(getattr(self, context_field))
        return lazy_format_string(format, context)

    def get_name(self):
        """
        Returns the name of this effect as a lazy i18n string
        """
        return self._get_lazy_i18n("name_format", "name_context")

    def set_name(self, format, context):
        """
        Sets the name of this effect to the value (format % context).
        """
        self._set_lazy_i18n("name_format", "name_context", format, context)

    def get_desc(self):
        """
        Returns the name of this effect as a lazy i18n string
        """
        return self._get_lazy_i18n("desc_format", "desc_context")

    def set_desc(self, format, context):
        """
        Sets the name of this effect to the value (format % context).
        """
        self._set_lazy_i18n("desc_format", "desc_context", format, context)
