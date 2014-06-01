# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'CopyEvent'
        db.delete_table(u'envaya_copyevent')

        # Deleting field 'Status.tmp_id'
        db.delete_column(u'envaya_status', 'tmp_id')


        # Changing field 'Status.id'
        db.alter_column(u'envaya_status', u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True))
        # Adding unique constraint on 'Status', fields [u'id']
        db.create_unique(u'envaya_status', [u'id'])

        # Deleting field 'SMS.tmp_id'
        db.delete_column(u'envaya_sms', 'tmp_id')


        # Changing field 'SMS.id'
        db.alter_column(u'envaya_sms', u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True))
        # Adding unique constraint on 'SMS', fields [u'id']
        db.create_unique(u'envaya_sms', [u'id'])


    def backwards(self, orm):
        # Removing unique constraint on 'SMS', fields [u'id']
        db.delete_unique(u'envaya_sms', [u'id'])

        # Removing unique constraint on 'Status', fields [u'id']
        db.delete_unique(u'envaya_status', [u'id'])

        # Adding model 'CopyEvent'
        db.create_table(u'envaya_copyevent', (
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('network', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('power', self.gf('django.db.models.fields.IntegerField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('battery', self.gf('django.db.models.fields.IntegerField')()),
            ('now', self.gf('django.db.models.fields.DateTimeField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'envaya', ['CopyEvent'])

        # Adding field 'Status.tmp_id'
        db.add_column(u'envaya_status', 'tmp_id',
                      self.gf('django.db.models.fields.IntegerField')(default=0, primary_key=True),
                      keep_default=False)


        # Changing field 'Status.id'
        db.alter_column(u'envaya_status', 'id', self.gf('django.db.models.fields.IntegerField')())
        # Adding field 'SMS.tmp_id'
        db.add_column(u'envaya_sms', 'tmp_id',
                      self.gf('django.db.models.fields.IntegerField')(default=0, primary_key=True),
                      keep_default=False)


        # Changing field 'SMS.id'
        db.alter_column(u'envaya_sms', 'id', self.gf('django.db.models.fields.IntegerField')())

    models = {
        u'envaya.sms': {
            'Meta': {'object_name': 'SMS'},
            'battery': ('django.db.models.fields.IntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'now': ('django.db.models.fields.DateTimeField', [], {}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'power': ('django.db.models.fields.IntegerField', [], {}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'envaya.status': {
            'Meta': {'object_name': 'Status'},
            'battery': ('django.db.models.fields.IntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'now': ('django.db.models.fields.DateTimeField', [], {}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone_status': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'power': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['envaya']
