# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Fund', fields ['code']
        db.delete_unique('app_fund', ['code'])

        # Changing field 'Fund.registration_date'
        db.alter_column('app_fund', 'registration_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True))

        # Adding unique constraint on 'Fund', fields ['contributer', 'code']
        db.create_unique('app_fund', ['contributer_id', 'code'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Fund', fields ['contributer', 'code']
        db.delete_unique('app_fund', ['contributer_id', 'code'])

        # Adding unique constraint on 'Fund', fields ['code']
        db.create_unique('app_fund', ['code'])

        # Changing field 'Fund.registration_date'
        db.alter_column('app_fund', 'registration_date', self.gf('django.db.models.fields.DateField')())


    models = {
        'app.companytype': {
            'Meta': {'object_name': 'CompanyType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'app.contributer': {
            'Meta': {'object_name': 'Contributer'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'hide': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'industry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Industry']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'app.fund': {
            'Meta': {'unique_together': "(('contributer', 'code'),)", 'object_name': 'Fund'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['app.FundCategory']", 'null': 'True'}),
            'classification': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['app.FundClassification']", 'null': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'comments': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'company_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['app.CompanyType']"}),
            'contributer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Contributer']"}),
            'funds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['app.Fund']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'investment_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['app.InvestmentType']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'registration_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'rrsp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sales_fee': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.FundType']"})
        },
        'app.fundcategory': {
            'Meta': {'object_name': 'FundCategory'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'app.fundclassification': {
            'Meta': {'object_name': 'FundClassification'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'app.fundtype': {
            'Meta': {'object_name': 'FundType'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'app.industry': {
            'Meta': {'object_name': 'Industry'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'app.investmenttype': {
            'Meta': {'object_name': 'InvestmentType'},
            'can_own': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['app.InvestmentType']", 'null': 'True'}),
            'company': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fund_of_fund': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'app.package': {
            'Meta': {'object_name': 'Package'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monthly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'per_file_price': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'quarterly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reports': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['app.Reports']", 'symmetrical': 'False'})
        },
        'app.reports': {
            'Meta': {'object_name': 'Reports'},
            'file_type': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'app.templateerror': {
            'Meta': {'object_name': 'TemplateError'},
            'column': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'error_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.IntegerField', [], {}),
            'valid_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.ValidTemplate']"})
        },
        'app.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Package']", 'null': 'True', 'blank': 'True'}),
            'page_code': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'receipt_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'app.uploadsetting': {
            'Meta': {'object_name': 'UploadSetting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stop_upload_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'upload_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'app.userlog': {
            'Meta': {'object_name': 'UserLog'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'blank': 'True'})
        },
        'app.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '14', 'blank': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'reports': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['app.Reports']", 'symmetrical': 'False'}),
            'suppressed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'user_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.UserType']", 'blank': 'True'})
        },
        'app.usertype': {
            'Meta': {'object_name': 'UserType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'app.validtemplate': {
            'Meta': {'object_name': 'ValidTemplate'},
            'contributer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Contributer']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template_one': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'template_three': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'template_two': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['app']
