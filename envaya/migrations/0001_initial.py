# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Event'
        db.create_table(u'envaya_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('now', self.gf('django.db.models.fields.DateTimeField')()),
            ('power', self.gf('django.db.models.fields.IntegerField')()),
            ('battery', self.gf('django.db.models.fields.IntegerField')()),
            ('network', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'envaya', ['Event'])

        # Adding model 'SMS'
        db.create_table(u'envaya_sms', (
            (u'event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['envaya.Event'], unique=True, primary_key=True)),
            ('sender', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'envaya', ['SMS'])

        # Adding model 'Status'
        db.create_table(u'envaya_status', (
            (u'event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['envaya.Event'], unique=True, primary_key=True)),
            ('phone_status', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'envaya', ['Status'])


    def backwards(self, orm):
        # Deleting model 'Event'
        db.delete_table(u'envaya_event')

        # Deleting model 'SMS'
        db.delete_table(u'envaya_sms')

        # Deleting model 'Status'
        db.delete_table(u'envaya_status')


    models = {
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