# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'EmailAddress'
        db.create_table('pasture_emailaddress', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('pasture', ['EmailAddress'])


    def backwards(self, orm):
        
        # Deleting model 'EmailAddress'
        db.delete_table('pasture_emailaddress')


    models = {
        'pasture.emailaddress': {
            'Meta': {'object_name': 'EmailAddress'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['pasture']
