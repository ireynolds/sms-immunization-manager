from datetime import datetime

from django.db import models

'''
Concrete to Abstract Inheritance
instructions from: http://www.markliu.me/2011/aug/23/migrating-a-django-postgres-db-from-concrete-inhe/
'''

def to_django_date(date):
	django_date_format = '%Y-%m-%d %H:%M:%S'
	if isinstance(date,basestring):
		date = int(date)
	return datetime.fromtimestamp(date/1000).strftime(django_date_format)

class Event(models.Model):
	
	phone_number = models.CharField(max_length=30)
	now = models.DateTimeField()
	power = models.IntegerField()
	battery = models.IntegerField()
	network = models.CharField(max_length=30)
	created = models.DateTimeField(auto_now=True)
	#id = models.IntegerField(primary_key=False)
	
	class Meta:
		abstract = True
	
	def __str__(self):
		out = 'Android: {0.phone_number} At: {0.now} Pow: {0.power} Bat: {0.battery}% Net: {0.network}'
		return out.format(self)
		
	def save(self):
		self.now = to_django_date(self.now)
		super(Event,self).save()
		
class SMS(Event):
	#tmp_id = models.IntegerField(primary_key=True)
	sender = models.CharField(max_length=30)
	message = models.CharField(max_length=500)
	timestamp = models.DateTimeField()
	
	def save(self):
		self.timestamp = to_django_date(self.timestamp)
		super(SMS,self).save()
	
	def __str__(self):
		return """From: {0.sender} At: {0.timestamp}
Message: {0.message}
{1}""".format(self,super(SMS,self).__str__())
		
	class Meta:
		verbose_name = "SMS"


class Status(Event):
	#tmp_id = models.IntegerField(primary_key=True)
	phone_status = models.CharField(max_length=50)
	
	def __str__(self):
		return """Status: {0.status}
{1}""".format(self,super(Status,self).__str__())

	class Meta:
		verbose_name_plural = "Statuses"
