# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding unique constraint on 'Contributer', fields ['code']
        db.create_unique('app_contributer', ['code'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Contributer', fields ['code']
        db.delete_unique('app_contributer', ['code'])


    models = {
        'app.contributer': {
            'Meta': {'object_name': 'Contributer'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'industry': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['app.Industry']", 'unique': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'app.industry': {
            'Meta': {'object_name': 'Industry'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        }
    }

    complete_apps = ['app']
