# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        """Copy value from distance field to event field as a string.
        """
        for brevet in orm.Brevet.objects.all():
            brevet.event = str(brevet.distance)
            brevet.save()


    def backwards(self, orm):
        """Copy brevet distance values from event field to distance field
           as integers.

           NOTE: Non-distance events can't be migrated backward, so a
           RuntimeError exception is also raised as a warning.
        """
        for brevet in orm.Brevet.objects.all():
            try:
                brevet.distance = int(brevet.event)
            except ValueError:
                brevet.distance = 0
            brevet.save()
        RuntimeError('Note: Non-distance events cannot be back-migrated!')

    models = {
        'register.brevet': {
            'Meta': {'object_name': 'Brevet'},
            'alt_start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'distance': ('django.db.models.fields.IntegerField', [], {}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_question': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'organizer_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'route_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'start_location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'start_time': ('django.db.models.fields.TimeField', [], {})
        },
        'register.rider': {
            'Meta': {'object_name': 'Rider'},
            'brevet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['register.Brevet']"}),
            'club_member': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_answer': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['register']
