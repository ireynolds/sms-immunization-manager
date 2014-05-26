from django.forms import ModelForm
from moderation.models import ModeratorProfile

class ModeratorAffiliationForm(ModelForm):
    class Meta:
        model = ModeratorProfile
        fields = ['node', 'facility',]