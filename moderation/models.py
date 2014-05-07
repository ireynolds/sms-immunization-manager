import json
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy
from django.utils.encoding import force_text
from django.utils.functional import lazy
from django.utils import six

def create_effect(is_successful, noop_i18n_name, name_context, noop_i18n_desc, desc_context):
    """
    Returns an un-saved MessageEffect with the given success state, name and description.
    noop_i18n_name contains the name of this effect as a format string returned from a noop i18n
    function. name_context is a dictionary mapping replacement items in noop_i18n_name to their
    values. The corresponding desc fields represent a message describing the outcome of this event.

    Every check or commit signal listener must return a MessageEffect instance created using this
    function or its shortcut functions below.
    """
    instance = MessageEffect()
    instance.success = is_successful
    instance.set_name(noop_i18n_name, name_context)
    instance.set_desc(noop_i18n_desc, desc_context)
    return instance

def success(noop_i18n_name, name_context, noop_i18n_desc, desc_context):
    """
    Returns an un-saved MessageEffect indicating a successful effect. See create_effect for a
    description of this function's parameters.
    """
    return create_effect(True, noop_i18n_name, name_context, noop_i18n_desc, desc_context)

def failure(noop_i18n_name, name_context, noop_i18n_desc, desc_context):
    """
    Returns an un-saved MessageEffect indicating an unsuccessful effect. See create_effect for a
    description of this function's parameters.
    """
    return create_effect(False, noop_i18n_name, name_context, noop_i18n_desc, desc_context)


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

    # If true, this effect was successful.
    success = models.BooleanField()

    # If true, this effect was created in the check phase of a message
    check_phase = models.BooleanField()

    # The name of this effect, as an untranslated format string
    name_format = models.TextField()
    # The context used to render name_format as a JSON-encoded dictionary
    name_context = models.TextField()

    # A description of this effect's outcome, as an untranslated format string
    desc_format = models.TextField()
    # The context used to render desc_format
    desc_context = models.TextField()

    def __unicode__(self):
        if self.success:
            outcome = ugettext("Success")
        else:
            outcome = ugettext("Failure")
        context = {"name": unicode(self.get_name()), "desc": unicode(self.get_desc())}
        return outcome + ugettext(": %(name)s: %(desc)s") % context

    def _set_lazy_i18n(self, format_field, context_field, format, context):
        # Ensure that every replacement string in format is a key in context
        format % context

        setattr(self, format_field, unicode(format))
        setattr(self, context_field, json.dumps(context))

    def _get_lazy_i18n(self, format_field, context_field):
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