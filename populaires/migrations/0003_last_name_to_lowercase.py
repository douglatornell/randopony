# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for rider in orm.Rider.objects.all():
            rider.lowercase_last_name = rider.last_name.lower()
            rider.save()


    def backwards(self, orm):
        pass


    models = {
        'populaires.populaire': {
            'Meta': {'ordering': "['date']", 'object_name': 'Populaire'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'distance': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'entry_form_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'entry_form_url_label': ('django.db.models.fields.CharField', [], {'default': "'Entry Form (PDF)'", 'max_length': '30', 'blank': 'True'}),
            'event_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'google_doc_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'organizer_email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'registration_closes': ('django.db.models.fields.DateTimeField', [], {}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'time': ('django.db.models.fields.TimeField', [], {})
        },
        'populaires.rider': {
            'Meta': {'ordering': "['lowercase_last_name']", 'object_name': 'Rider'},
            'distance': ('django.db.models.fields.IntegerField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'lowercase_last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'populaire': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['populaires.Populaire']"})
        }
    }

    complete_apps = ['populaires']
