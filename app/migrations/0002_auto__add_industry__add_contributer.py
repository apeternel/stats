# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Industry'
        db.create_table('app_industry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('app', ['Industry'])

        # Adding model 'Contributer'
        db.create_table('app_contributer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('industry', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.Industry'], unique=True)),
        ))
        db.send_create_signal('app', ['Contributer'])


    def backwards(self, orm):
        
        # Deleting model 'Industry'
        db.delete_table('app_industry')

        # Deleting model 'Contributer'
        db.delete_table('app_contributer')


    models = {
        'app.contributer': {
            'Meta': {'object_name': 'Contributer'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
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
