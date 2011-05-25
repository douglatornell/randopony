# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Populaire'
        db.create_table('populaires_populaire', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('distance', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('time', self.gf('django.db.models.fields.TimeField')()),
            ('organizer_email', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('registration_closes', self.gf('django.db.models.fields.DateTimeField')()),
            ('entry_form_url', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('entry_form_url_label', self.gf('django.db.models.fields.CharField')(default='Entry Form (PDF)', max_length=30, blank=True)),
            ('google_doc_id', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('populaires', ['Populaire'])

        # Adding model 'Rider'
        db.create_table('populaires_rider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('distance', self.gf('django.db.models.fields.IntegerField')()),
            ('populaire', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['populaires.Populaire'])),
        ))
        db.send_create_signal('populaires', ['Rider'])


    def backwards(self, orm):
        
        # Deleting model 'Populaire'
        db.delete_table('populaires_populaire')

        # Deleting model 'Rider'
        db.delete_table('populaires_rider')


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
            'Meta': {'ordering': "['last_name']", 'object_name': 'Rider'},
            'distance': ('django.db.models.fields.IntegerField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'populaire': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['populaires.Populaire']"})
        }
    }

    complete_apps = ['populaires']
