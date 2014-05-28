from django.forms import ModelForm
from moderation.models import ModeratorProfile
from user_registration.models import ContactProfile
from rapidsms.models import Contact, Connection
from django.forms.models import inlineformset_factory

class ModeratorAffiliationForm(ModelForm):
    class Meta:
        model = ModeratorProfile
        fields = ['node', 'facility',]

class ContactForm(ModelForm):
    class Meta:
        model = Contact

ContactProfileFormSet = inlineformset_factory(Contact, ContactProfile, extra=0, can_delete=False)
ConnectionFormSet = inlineformset_factory(Contact, Connection, extra=1)