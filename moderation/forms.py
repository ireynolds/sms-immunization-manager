from django import forms
from django.conf import settings
from rapidsms.router import lookup_connections
from moderation.models import ModeratorProfile
from user_registration.models import ContactProfile
from rapidsms.models import Contact, Connection
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _

class ModeratorAffiliationForm(forms.ModelForm):
    class Meta:
        model = ModeratorProfile
        fields = ['node', 'facility',]

class ContactForm(forms.ModelForm):
    """
    A form for editing a contact. Includes behavior for settings a contact's phone number by way
    of a Connection. This form is somewhat of a hack, and is a symptom of using RapidSMS' built-in
    Connection and Contact models.
    """
    phone_number = forms.CharField(max_length=100, required=False)

    # Override the language widget to be restricted to settings.LANGUAGES
    language = forms.ChoiceField(choices=settings.LANGUAGES)

    class Meta:
        model = Contact

    def __init__(self, *args, **kwargs):
        """
        Set the initial value of phone_number to be the Contact instance's phone number.
        """
        if 'instance' in kwargs:
            initial = kwargs.get('initial', {})
            initial['phone_number'] = kwargs['instance'].contactprofile.get_phone_number()
            kwargs['initial'] = initial

        super(ContactForm, self).__init__(*args, **kwargs)


    def clean_phone_number(self):
        """
        Verifies that the form's phone number is not in use
        """
        number = self.cleaned_data['phone_number']
        if Connection.objects.filter(identity=number).exclude(contact=None)\
                .exclude(contact__pk=self.instance.pk).exists():
            raise forms.ValidationError(_("This number is already in use by another contact"))

        return number

    def save(self, *args, **kwargs):
        # Save the Contact's fields, and get the saved instance
        instance = super(ContactForm, self).save(*args, **kwargs)

        # Short-circuit if the user wishes to clear the contact's phone number
        if self.cleaned_data['phone_number'] == '':
            instance.connection_set.update(contact=None)
            return instance

        # Obtain Connection instances for the phone and moderator backends. If contact instances
        # do not already exist, they are created by lookup_connections
        phone_connection = lookup_connections(settings.PHONE_BACKEND, 
            [self.cleaned_data['phone_number']])[0]
        moderator_connection = lookup_connections(settings.MODERATOR_BACKEND, 
            [self.cleaned_data['phone_number']])[0]

        # Assert that these connections are not in use by another contact. This should be enforced
        # by clean_phone_number, and should always pass (assuming cleaning and saving are done in
        # the same database transaction).
        assert phone_connection.contact == None or phone_connection.contact == instance
        assert moderator_connection.contact == None or moderator_connection.contact == instance

        # Update any existing connections that reference the saved contact
        instance.connection_set.update(contact=None)

        # Update the connections to reference the saved contact.
        phone_connection.contact = instance
        phone_connection.save()
        moderator_connection.contact = instance
        moderator_connection.save()

        # Return the contact instance, to satisfy the spec of save()
        return instance

class ContactProfileForm(forms.ModelForm):
    class Meta:
        model = ContactProfile
        fields = ['role_name', 'facility']

class ResendForm(forms.Form):
    """
    A form for re-sending an SMS message
    """
    text = forms.CharField(widget=forms.Textarea)