# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

	def forwards(self, orm):
		"Write your forwards methods here."
		# Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
		for event in orm.Event.objects.all():
			copy = orm.CopyEvent()
			copy.battery = event.battery
			copy.created = event.created
			copy.id = event.id
			copy.network = event.network
			copy.now = event.now
			copy.phone_number = event.phone_number
			copy.power = event.power
			copy.save()

	def backwards(self, orm):
		"Write your backwards methods here."
		orm.CopyEvent.objects.all().delete()

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
		u'envaya.event': {
			'Meta': {'object_name': 'Event'},
			'battery': ('django.db.models.fields.IntegerField', [], {}),
			'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'network': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
			'now': ('django.db.models.fields.DateTimeField', [], {}),
			'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
			'power': ('django.db.models.fields.IntegerField', [], {})
		},
		u'envaya.sms': {
			'Meta': {'object_name': 'SMS', '_ormbases': [u'envaya.Event']},
			u'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['envaya.Event']", 'unique': 'True', 'primary_key': 'True'}),
			'message': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
			'sender': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
			'timestamp': ('django.db.models.fields.DateTimeField', [], {})
		},
		u'envaya.status': {
			'Meta': {'object_name': 'Status', '_ormbases': [u'envaya.Event']},
			u'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['envaya.Event']", 'unique': 'True', 'primary_key': 'True'}),
			'phone_status': ('django.db.models.fields.CharField', [], {'max_length': '50'})
		}
	}

	complete_apps = ['envaya']
	symmetrical = True
