# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'StructureTimeSeries'
        db.create_table('app_structuretimeseries', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.CompanyType'])),
            ('net_assets', self.gf('django.db.models.fields.FloatField')()),
            ('cash', self.gf('django.db.models.fields.FloatField')()),
            ('gross_sales', self.gf('django.db.models.fields.FloatField')()),
            ('reinvested_distribution', self.gf('django.db.models.fields.FloatField')()),
            ('gross_redemptions', self.gf('django.db.models.fields.FloatField')()),
            ('transfers_in', self.gf('django.db.models.fields.FloatField')()),
            ('transfers_out', self.gf('django.db.models.fields.FloatField')()),
            ('unit_holder_accounts', self.gf('django.db.models.fields.FloatField')()),
            ('capital_gains', self.gf('django.db.models.fields.FloatField')()),
            ('other_income', self.gf('django.db.models.fields.FloatField')()),
            ('net_new_money', self.gf('django.db.models.fields.FloatField')()),
            ('sales_exec', self.gf('django.db.models.fields.FloatField')()),
            ('fund_count', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('app', ['StructureTimeSeries'])


    def backwards(self, orm):
        
        # Deleting model 'StructureTimeSeries'
        db.delete_table('app_structuretimeseries')


    models = {
        'app.assetclasstimeseries': {
            'Meta': {'object_name': 'AssetClassTimeSeries'},
            'asset_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.FundType']"}),
            'capital_gains': ('django.db.models.fields.FloatField', [], {}),
            'cash': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fund_count': ('django.db.models.fields.IntegerField', [], {}),
            'gross_redemptions': ('django.db.models.fields.FloatField', [], {}),
            'gross_sales': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'net_assets': ('django.db.models.fields.FloatField', [], {}),
            'net_new_money': ('django.db.models.fields.FloatField', [], {}),
            'other_income': ('django.db.models.fields.FloatField', [], {}),
            'reinvested_distribution': ('django.db.models.fields.FloatField', [], {}),
            'sales_exec': ('django.db.models.fields.FloatField', [], {}),
            'transfers_in': ('django.db.models.fields.FloatField', [], {}),
            'transfers_out': ('django.db.models.fields.FloatField', [], {}),
            'unit_holder_accounts': ('django.db.models.fields.FloatField', [], {})
        },
        'app.cifsccategorytimeseries': {
            'Meta': {'object_name': 'CIFSCCategoryTimeSeries'},
            'capital_gains': ('django.db.models.fields.FloatField', [], {}),
            'cash': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fund_count': ('django.db.models.fields.IntegerField', [], {}),
            'fund_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.FundType']"}),
            'gross_redemptions': ('django.db.models.fields.FloatField', [], {}),
            'gross_sales': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'net_assets': ('django.db.models.fields.FloatField', [], {}),
            'net_new_money': ('django.db.models.fields.FloatField', [], {}),
            'other_income': ('django.db.models.fields.FloatField', [], {}),
            'reinvested_distribution': ('django.db.models.fields.FloatField', [], {}),
            'sales_exec': ('django.db.models.fields.FloatField', [], {}),
            'transfers_in': ('django.db.models.fields.FloatField', [], {}),
            'transfers_out': ('django.db.models.fields.FloatField', [], {}),
            'unit_holder_accounts': ('django.db.models.fields.FloatField', [], {})
        },
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
            'Meta': {'object_name': 'Fund'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['app.FundCategory']", 'null': 'True'}),
            'classification': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['app.FundClassification']", 'null': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'comments': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'company_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['app.CompanyType']"}),
            'contributer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Contributer']"}),
            'funds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['app.Fund']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'investment_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['app.InvestmentType']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'registration_date': ('django.db.models.fields.DateField', [], {}),
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
        'app.indextimeseries': {
            'Meta': {'object_name': 'IndexTimeSeries'},
            'capital_gains': ('django.db.models.fields.FloatField', [], {}),
            'cash': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fund_count': ('django.db.models.fields.IntegerField', [], {}),
            'gross_redemptions': ('django.db.models.fields.FloatField', [], {}),
            'gross_sales': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'net_assets': ('django.db.models.fields.FloatField', [], {}),
            'net_new_money': ('django.db.models.fields.FloatField', [], {}),
            'other_income': ('django.db.models.fields.FloatField', [], {}),
            'reinvested_distribution': ('django.db.models.fields.FloatField', [], {}),
            'sales_exec': ('django.db.models.fields.FloatField', [], {}),
            'transfers_in': ('django.db.models.fields.FloatField', [], {}),
            'transfers_out': ('django.db.models.fields.FloatField', [], {}),
            'unit_holder_accounts': ('django.db.models.fields.FloatField', [], {})
        },
        'app.industry': {
            'Meta': {'object_name': 'Industry'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'app.investmentproducttypetimeseries': {
            'Meta': {'object_name': 'InvestmentProductTypeTimeSeries'},
            'capital_gains': ('django.db.models.fields.FloatField', [], {}),
            'cash': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fund_count': ('django.db.models.fields.IntegerField', [], {}),
            'gross_redemptions': ('django.db.models.fields.FloatField', [], {}),
            'gross_sales': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.InvestmentType']"}),
            'net_assets': ('django.db.models.fields.FloatField', [], {}),
            'net_new_money': ('django.db.models.fields.FloatField', [], {}),
            'other_income': ('django.db.models.fields.FloatField', [], {}),
            'reinvested_distribution': ('django.db.models.fields.FloatField', [], {}),
            'sales_exec': ('django.db.models.fields.FloatField', [], {}),
            'transfers_in': ('django.db.models.fields.FloatField', [], {}),
            'transfers_out': ('django.db.models.fields.FloatField', [], {}),
            'unit_holder_accounts': ('django.db.models.fields.FloatField', [], {})
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
            'annual_price': ('django.db.models.fields.FloatField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'per_file_price': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True'})
        },
        'app.structuretimeseries': {
            'Meta': {'object_name': 'StructureTimeSeries'},
            'capital_gains': ('django.db.models.fields.FloatField', [], {}),
            'cash': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fund_count': ('django.db.models.fields.IntegerField', [], {}),
            'gross_redemptions': ('django.db.models.fields.FloatField', [], {}),
            'gross_sales': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'net_assets': ('django.db.models.fields.FloatField', [], {}),
            'net_new_money': ('django.db.models.fields.FloatField', [], {}),
            'other_income': ('django.db.models.fields.FloatField', [], {}),
            'reinvested_distribution': ('django.db.models.fields.FloatField', [], {}),
            'sales_exec': ('django.db.models.fields.FloatField', [], {}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.CompanyType']"}),
            'transfers_in': ('django.db.models.fields.FloatField', [], {}),
            'transfers_out': ('django.db.models.fields.FloatField', [], {}),
            'unit_holder_accounts': ('django.db.models.fields.FloatField', [], {})
        },
        'app.templateerror': {
            'Meta': {'object_name': 'TemplateError'},
            'error': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.IntegerField', [], {}),
            'valid_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.ValidTemplate']"})
        },
        'app.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Package']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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
            'member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '14', 'blank': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
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
