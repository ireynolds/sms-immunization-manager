# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Event'
        db.delete_table(u'envaya_event')

        # Deleting field 'Status.event_ptr'
        db.delete_column(u'envaya_status', u'event_ptr_id')

        # Adding field 'Status.phone_number'
        db.add_column(u'envaya_status', 'phone_number',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30),
                      keep_default=False)

        # Adding field 'Status.now'
        db.add_column(u'envaya_status', 'now',
                      self.gf('django.db.models.fields.DateTimeField')(default = datetime.datetime.now()),
                      keep_default=False)

        # Adding field 'Status.power'
        db.add_column(u'envaya_status', 'power',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Status.battery'
        db.add_column(u'envaya_status', 'battery',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Status.network'
        db.add_column(u'envaya_status', 'network',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30),
                      keep_default=False)

        # Adding field 'Status.created'
        db.add_column(u'envaya_status', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default = datetime.datetime.now()),
                      keep_default=False)

        # Adding field 'Status.id'
        db.add_column(u'envaya_status', 'id',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Deleting field 'SMS.event_ptr'
        db.delete_column(u'envaya_sms', u'event_ptr_id')

        # Adding field 'SMS.phone_number'
        db.add_column(u'envaya_sms', 'phone_number',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30),
                      keep_default=False)

        # Adding field 'SMS.now'
        db.add_column(u'envaya_sms', 'now',
                      self.gf('django.db.models.fields.DateTimeField')(default = datetime.datetime.now()),
                      keep_default=False)

        # Adding field 'SMS.power'
        db.add_column(u'envaya_sms', 'power',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'SMS.battery'
        db.add_column(u'envaya_sms', 'battery',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'SMS.network'
        db.add_column(u'envaya_sms', 'network',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30),
                      keep_default=False)

        # Adding field 'SMS.created'
        db.add_column(u'envaya_sms', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default = datetime.datetime.now()),
                      keep_default=False)

        # Adding field 'SMS.id'
        db.add_column(u'envaya_sms', 'id',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


	def backwards(self, orm):
		# Adding model 'Event'
		db.create_table(u'envaya_event', (
			('phone_number', self.gf('django.db.models.fields.CharField')(max_length=30)),
			('network', self.gf('django.db.models.fields.CharField')(max_length=30)),
			('power', self.gf('django.db.models.fields.IntegerField')()),
			('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
			('battery', self.gf('django.db.models.fields.IntegerField')()),
			('now', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
			(u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
		))
		db.send_create_signal(u'envaya', ['Event'])

		# Adding field 'Status.event_ptr'
		db.add_column(u'envaya_status', u'event_ptr',
					  self.gf('django.db.models.fields.related.OneToOneField')(default=0, to=orm['envaya.Event'], unique=True),
					  keep_default=False)
					  

		# Deleting field 'Status.phone_number'
		db.delete_column(u'envaya_status', 'phone_number')

		# Deleting field 'Status.now'
		db.delete_column(u'envaya_status', 'now')

		# Deleting field 'Status.power'
		db.delete_column(u'envaya_status', 'power')

		# Deleting field 'Status.battery'
		db.delete_column(u'envaya_status', 'battery')

		# Deleting field 'Status.network'
		db.delete_column(u'envaya_status', 'network')

		# Deleting field 'Status.created'
		db.delete_column(u'envaya_status', 'created')

		# Deleting field 'Status.id'
		db.delete_column(u'envaya_status', 'id')

		# Adding field 'SMS.event_ptr'
		db.add_column(u'envaya_sms', u'event_ptr',
					  self.gf('django.db.models.fields.related.OneToOneField')(default=0, to=orm['envaya.Event'], unique=True),
					  keep_default=False)

		# Deleting field 'SMS.phone_number'
		db.delete_column(u'envaya_sms', 'phone_number')

		# Deleting field 'SMS.now'
		db.delete_column(u'envaya_sms', 'now')

		# Deleting field 'SMS.power'
		db.delete_column(u'envaya_sms', 'power')

		# Deleting field 'SMS.battery'
		db.delete_column(u'envaya_sms', 'battery')

		# Deleting field 'SMS.network'
		db.delete_column(u'envaya_sms', 'network')

		# Deleting field 'SMS.created'
		db.delete_column(u'envaya_sms', 'created')

		# Deleting field 'SMS.id'
		db.delete_column(u'envaya_sms', 'id')


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
            'now': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
            'now': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone_status': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'power': ('django.db.models.fields.IntegerField', [], {}),
            'tmp_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['envaya']
