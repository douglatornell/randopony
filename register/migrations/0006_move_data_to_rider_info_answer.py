# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        """Copy data from rider qual_info field to info_answer field.
        """
        for rider in orm.Rider.objects.all():
            rider.info_answer = rider.qual_info
            rider.save()


    def backwards(self, orm):
        """Copy data from rider info_answer field to qual_info field.
        """
        for rider in orm.Rider.objects.all():
            rider.qual_info = rider.info_answer
            rider.save()


    models = {
        'register.brevet': {
            'Meta': {'object_name': 'Brevet'},
            'alt_start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'distance': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_question': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'organizer_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'qual_info_question': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'qual_info': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['register']
