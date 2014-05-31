#python imports
import logging, pprint, json, traceback

#django imports
from django.views.generic.edit import FormView
from django.views.generic.base import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

#rapidsms imports
from rapidsms.router import receive, lookup_connections, send

#envaya imports
from .forms import EnvayaForm
import models
logger = logging.getLogger(__name__)

class EnvayaView(View):
	
	backend_name = None
	http_method_names = ['post']
	
	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		"""
		Wraps the main entry point into the view with the csrf_exempt
		decorator, which most (if not all) clients using this view will not
		know about.
		"""
		logger.debug("Dispatch: \n\tPOST:%s\n\tFrom: %s",args[0].POST,args[0].META['HTTP_USER_AGENT'])
		if 'backend_name' in kwargs:
			self.backend_name = kwargs['backend_name']
		return super(EnvayaView, self).dispatch(*args, **kwargs)
		
	def post(self,request):
		logger.debug("Enter Post")
		action = request.POST.get('action',None)
		if action:
			try:
				if action=="incoming":
					#only parse sms messages not calls or mms
					if request.POST.get('message_type',None)=='sms':
						return self.handle_message()
					else:
						return HttpResponseBadRequest('only sms messages supported [400]')
				elif action=="device_status":
					event_kwargs = self.get_model_kwargs('status')
					event_kwargs['phone_status'] = event_kwargs.pop('status')
					print event_kwargs
					#models.Status(**event_kwargs).save()
					return HttpResponse('Status Recieved')
				elif action=="test":
					return HttpResponse('Test Ok')
				else:
					return HttpResponseNotFound('action not implemented [404]')
			except KeyError as e:
				logger.debug("Required POST value missing. "+str(e))
				traceback.print_exc()
				return HttpResponseBadRequest("Required POST value missing. "+str(e))
		else:
			return HttpResponseBadRequest('action required [400]')
	
	def get_model_kwargs(self,*extra_values): #throws KeyError
		#add extra values to base values
		print extra_values
		event_values = ['phone_number','network','now','battery','power']
		event_values.extend(extra_values)
		#make kwarg dict of event name and request post value
		return {value:self.request.POST[value] for value in event_values}
		
	def handle_message(self):
		event_kwargs = self.get_model_kwargs('from','message','timestamp')
		#fix variables for model 
		event_kwargs['sender'] = event_kwargs.pop('from')
		connection = lookup_connections('envaya', [event_kwargs['sender']])[0]
		msg_in = receive(event_kwargs['message'],connection)
		#send response via http call back
		events = [{'event':'send','messages':[],},]
		msgs_out = []
		for response in msg_in.responses:
			#msgs_out.append(send(**response)) #send is called when we process the msg, no need to call it again here
			events[0]['messages'].append({
				'to':response['connections'][0].identity,
				'message':response['text']
				})
		#models.SMS(**event_kwargs).save()
		logger.debug("Send Envaya:\n%s",json.dumps({'events':events}))
		return HttpResponse(json.dumps({'events':events}),mimetype='application/json')

		
class TestView(FormView):
	
	form_class = EnvayaForm
	template_name = "envaya_test.html"
	backend_name = None
	
	def get_form_kwargs(self):
		"""Always pass backend_name into __init__"""
		kwargs = super(TestView, self).get_form_kwargs()
		kwargs['backend_name'] = self.backend_name
		return kwargs
		
	def form_valid(self, form):
		if self.request.method == 'GET':
			self.request.POST = self.request.GET.copy()
		#self.request.POST = self.request.POST.copy()
		#self.request.POST.pop('battery')
		return EnvayaView.as_view(backend_name="envaya")(self.request)
		return HttpResponse("<pre>%s</pre>"%(pprint.pformat(form.cleaned_data),))
