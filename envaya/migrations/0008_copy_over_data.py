# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

	def forwards(self, orm):
		"Write your forwards methods here."
		# Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
		for sms in orm.SMS.objects.all():
			copy = orm.CopyEvent.objects.get(pk=sms.tmp_id)
			sms.battery = copy.battery
			sms.created = copy.created
			sms.network = copy.network
			sms.now = copy.now
			sms.phone_number = copy.phone_number
			sms.power = copy.power
			sms.id = sms.tmp_id
			sms.save()
			
		for status in orm.Status.objects.all():
			copy = orm.CopyEvent.objects.get(pk=sms.tmp_id)
			status.battery = copy.battery
			status.created = copy.created
			status.network = copy.network
			status.now = copy.now
			status.phone_number = copy.phone_number
			status.power = copy.power
			status.id = status.tmp_id
			status.save()
			

	def backwards(self, orm):
		"Write your backwards methods here."
		

	models = {
		u'envaya.copyevent': {
			'Meta': {'object_name': 'CopyEvent'},
			'battery': ('django.db.models.fields.IntegerField', [], {}),
			'created': ('django.db.models.fields.DateTimeField', [], {}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'network': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
			'now': ('django.db.models.fields.DateTimeField', [], {}),
			'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
			'power': ('django.db.models.fields.IntegerField', [], {})
		},
		u'envaya.sms': {
			'Meta': {'object_name': 'SMS'},
			'battery': ('django.db.models.fields.IntegerField', [], {}),
			'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
			'id': ('django.db.models.fields.IntegerField', [], {}),
			'message': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
			'network': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
			'now': ('django.db.models.fields.DateTimeField', [], {}),
			'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
			'power': ('django.db.models.fields.IntegerField', [], {}),
			'sender': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
			'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
			'tmp_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
		},
		u'envaya.status': {
			'Meta': {'object_name': 'Status'},
			'battery': ('django.db.models.fields.IntegerField', [], {}),
			'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
			'id': ('django.db.models.fields.IntegerField', [], {}),
			'network': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
			'now': ('django.db.models.fields.DateTimeField', [], {}),
			'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
			'phone_status': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
			'power': ('django.db.models.fields.IntegerField', [], {}),
			'tmp_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
		}
	}

	complete_apps = ['envaya']
	symmetrical = True
