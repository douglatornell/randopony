# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Brevet.info_question'
        db.add_column('register_brevet', 'info_question', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Brevet.info_question'
        db.delete_column('register_brevet', 'info_question')


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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'qual_info': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['register']
