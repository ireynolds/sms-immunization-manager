# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Status.event_ptr'
        db.alter_column(u'envaya_status', u'event_ptr_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['envaya.Event'], unique=True))

        # Changing field 'Status.tmp_id'
        db.alter_column(u'envaya_status', 'tmp_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True))
        # Adding unique constraint on 'Status', fields ['tmp_id']
        db.create_unique(u'envaya_status', ['tmp_id'])


        # Changing field 'SMS.event_ptr'
        db.alter_column(u'envaya_sms', u'event_ptr_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['envaya.Event'], unique=True))

        # Changing field 'SMS.tmp_id'
        db.alter_column(u'envaya_sms', 'tmp_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True))
        # Adding unique constraint on 'SMS', fields ['tmp_id']
        db.create_unique(u'envaya_sms', ['tmp_id'])


        # Changing field 'Event.now'
        db.alter_column(u'envaya_event', 'now', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

    def backwards(self, orm):
        # Removing unique constraint on 'SMS', fields ['tmp_id']
        db.delete_unique(u'envaya_sms', ['tmp_id'])

        # Removing unique constraint on 'Status', fields ['tmp_id']
        db.delete_unique(u'envaya_status', ['tmp_id'])


        # Changing field 'Status.event_ptr'
        db.alter_column(u'envaya_status', u'event_ptr_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['envaya.Event'], unique=True, primary_key=True))

        # Changing field 'Status.tmp_id'
        db.alter_column(u'envaya_status', 'tmp_id', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'SMS.event_ptr'
        db.alter_column(u'envaya_sms', u'event_ptr_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['envaya.Event'], unique=True, primary_key=True))

        # Changing field 'SMS.tmp_id'
        db.alter_column(u'envaya_sms', 'tmp_id', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Event.now'
        db.alter_column(u'envaya_event', 'now', self.gf('django.db.models.fields.DateTimeField')())

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
            'now': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'power': ('django.db.models.fields.IntegerField', [], {})
        },
        u'envaya.sms': {
            'Meta': {'object_name': 'SMS', '_ormbases': [u'envaya.Event']},
            u'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['envaya.Event']", 'unique': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'tmp_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        u'envaya.status': {
            'Meta': {'object_name': 'Status', '_ormbases': [u'envaya.Event']},
            u'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['envaya.Event']", 'unique': 'True'}),
            'phone_status': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tmp_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['envaya']