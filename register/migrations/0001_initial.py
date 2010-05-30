# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Brevet'
        db.create_table('register_brevet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('distance', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('route_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('start_location', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('start_time', self.gf('django.db.models.fields.TimeField')()),
            ('organizer_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('qual_info_question', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('register', ['Brevet'])

        # Adding model 'Rider'
        db.create_table('register_rider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('club_member', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('qual_info', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('brevet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['register.Brevet'])),
        ))
        db.send_create_signal('register', ['Rider'])


    def backwards(self, orm):
        
        # Deleting model 'Brevet'
        db.delete_table('register_brevet')

        # Deleting model 'Rider'
        db.delete_table('register_rider')


    models = {
        'register.brevet': {
            'Meta': {'object_name': 'Brevet'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'distance': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
