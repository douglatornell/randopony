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
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('time', self.gf('django.db.models.fields.TimeField')()),
            ('organizer_email', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('info_question', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('google_doc_id', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('event', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('route_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('alt_start_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('register', ['Brevet'])

        # Adding model 'ClubEvent'
        db.create_table('register_clubevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('time', self.gf('django.db.models.fields.TimeField')()),
            ('organizer_email', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('info_question', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('google_doc_id', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('event', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('register', ['ClubEvent'])

        # Adding model 'BrevetRider'
        db.create_table('register_brevetrider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('info_answer', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('club_member', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('brevet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['register.Brevet'])),
        ))
        db.send_create_signal('register', ['BrevetRider'])

        # Adding model 'EventParticipant'
        db.create_table('register_eventparticipant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('info_answer', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['register.ClubEvent'])),
        ))
        db.send_create_signal('register', ['EventParticipant'])


    def backwards(self, orm):
        
        # Deleting model 'Brevet'
        db.delete_table('register_brevet')

        # Deleting model 'ClubEvent'
        db.delete_table('register_clubevent')

        # Deleting model 'BrevetRider'
        db.delete_table('register_brevetrider')

        # Deleting model 'EventParticipant'
        db.delete_table('register_eventparticipant')


    models = {
        'register.brevet': {
            'Meta': {'ordering': "['date']", 'object_name': 'Brevet'},
            'alt_start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'google_doc_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_question': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'organizer_email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'route_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'time': ('django.db.models.fields.TimeField', [], {})
        },
        'register.brevetrider': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'BrevetRider'},
            'brevet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['register.Brevet']"}),
            'club_member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_answer': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'register.clubevent': {
            'Meta': {'ordering': "['date']", 'object_name': 'ClubEvent'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'google_doc_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_question': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'organizer_email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'time': ('django.db.models.fields.TimeField', [], {})
        },
        'register.eventparticipant': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'EventParticipant'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['register.ClubEvent']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_answer': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['register']
