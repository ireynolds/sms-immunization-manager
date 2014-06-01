import logging

from django.forms import widgets

from django import forms


#rapidsms imports
from rapidsms.backends.http.forms import BaseHttpForm

logger = logging.getLogger(__name__)

class EnvayaForm(BaseHttpForm):
	
	
	phone_number = forms.CharField(initial="1111-test")
	action = forms.CharField(initial="incoming")
	#now = forms.DateTimeField(initial="1390433250705",input_formats=["%U%u"])
	now = forms.CharField(initial="1390433250705")
	
	log = forms.CharField(widget=widgets.Textarea,required=False)
	power = forms.IntegerField(initial="0")
	battery = forms.IntegerField(initial="0")
	network = forms.CharField(initial="WIFI")
	
	#message options
	
	message_type = forms.CharField(required=False,initial="sms")
	message = forms.CharField(required=False,initial="Test message")
	#timestamp = forms.DateTimeField(initial="1390433248000",input_formats=["%U%u"])
	timestamp = forms.CharField(initial="1390433248000")
	
	def __init__(self,*args,**kwargs):
		super(EnvayaForm,self).__init__(*args,**kwargs)
		self.fields['from'] = forms.CharField(initial="+17034753316")
		
	def get_incoming_data(self):
		fields = self.cleaned_data.copy()
		# save message_id as external_id so RapidSMS will handle it properly
		#fields['external_id'] = self.cleaned_data['message_id']
		#connections = self.lookup_connections([self.cleaned_data['from']])
		return {'identity': self.cleaned_data['from'],
			'text': self.cleaned_data['message'],
			'fields': fields}
	
	
