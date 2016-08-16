# Ajax Views

import csv
import datetime
import os
import settings
import locale
import urllib2
import urllib
from xml.dom.minidom import parse, parseString
from datetime import date, datetime, timedelta


# Django libs
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext

from app.views.views import check_user_permissions, send_email
from settings import GATEWAY, GATEWAY_URL

from django.core.mail import send_mail


# Models
from app.models import CompanyType,  FundCategory, UploadSetting, AllowedTemplate,\
Industry, InvestmentType, Contributer, Fund, FundType, TemplateError, UserLog, UserProfile, UserType, ValidTemplate, Transaction, Package, Reports

#from app.tasks import generate_standalone_view

from celery.task import task

@task
def generate_standalone_view(suppressed, estimated):
    warnings = []
    response = { }
    errors = []
    
    try:
        setting = UploadSetting.objects.get(pk=1)
        date = setting.upload_date.strftime('%Y-%m')
    except UploadSetting.DoesNotExist:
        errors.append('Upload date not defined')
    

    if suppressed == True:
        contributers = Contributer.objects.all()
    else:
        contributers = Contributer.objects.filter(hide=False)
    template_data = list()
    report_data = list()
    
    report_data = add_ific_header(report_data)
    
    for contributer in contributers:        
        file_name = '%s_template1' % date
        
        file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, contributer.id, file_name)
            

        if os.path.isfile(file_path):
            
            with open(file_path, 'U') as csv_file:   
                template_data = list(csv.reader(csv_file, dialect='excel-tab'))
                 
            
            index = 0
            # Contributer Totals
            net_assets_total = 0.00
            cash_total = 0.00
            gross_sales_total = 0.00
            reinvested_distribution_total = 0.00
            gross_redemptions_total = 0.00
            transfers_in_total = 0.00
            transfers_out_total = 0.00
            net_sales_total = 0.00
            net_new_money_total = 0.00
            unitholder_total = 0
            capital_gains_total = 0.00
            other_income_total = 0.00
            
            for fund_code in template_data[1]:
                
                if len(fund_code) <= 3:
                    
                    try:
                        
                        fund = Fund.objects.get(code=fund_code.lower(), contributer=contributer)
                        
                        if fund.investment_type.fund_of_fund == False:
                            
                            fund_data = get_column_data(template_data, index)
                            
                            ific_code = '%s*%s' % (contributer.code.upper(), fund.code.upper())
                            fund_structure = fund.company_type.name
                            fund_classification = fund.classification.name
                            fund_index = 'Yes' if fund.index else 'No'
                            sales_fee = 0
                            fund_name = fund.name.replace(',', '')
                            for s in Fund.SALES_FEE_CHOICES:
                                if s[0] == fund.sales_fee:
                                    sales_fee = s[1]
                                    break
                                
                            net_assets = float(fund_data[2].replace(',', '').replace('"', '').replace('$', ''))    
                            cash = float(fund_data[3].replace(',', '').replace('"', '').replace('$', ''))
                            gross_sales = float(fund_data[4].replace(',', '').replace('"', '').replace('$', ''))
                            reinvested_distribution = float(fund_data[5].replace(',', '').replace('"', '').replace('$', ''))
                            gross_redemptions = float(fund_data[6].replace(',', '').replace('"', '').replace('$', ''))
                            transfers_in = float(fund_data[7].replace(',', '').replace('"', '').replace('$', ''))
                            transfers_out = float(fund_data[8].replace(',', '').replace('"', '').replace('$', ''))
                            net_sales = gross_sales - gross_redemptions + transfers_in - transfers_out
                            unitholder = int(fund_data[10].replace(',', '').replace('"', '').replace('$', ''))
                            capital_gains = float(fund_data[11].replace(',', '').replace('"', '').replace('$', ''))
                            net_new_money = gross_sales - gross_redemptions
                            other_income = float(fund_data[12].replace(',', '').replace('"', '').replace('$', ''))
                            net_sales_inc = gross_sales + reinvested_distribution - gross_redemptions + transfers_in - transfers_out
                            
                            net_assets_total = net_assets_total + net_assets
                            cash_total = cash_total + cash
                            gross_sales_total = gross_sales_total + gross_sales
                            reinvested_distribution_total = reinvested_distribution_total + reinvested_distribution
                            gross_redemptions_total = gross_redemptions_total + gross_redemptions
                            transfers_in_total = transfers_in_total + transfers_in
                            transfers_out_total = transfers_out_total + transfers_out
                            net_sales_total = net_sales_total + net_sales
                            unitholder_total = unitholder_total + unitholder
                            capital_gains_total = capital_gains_total + capital_gains
                            net_new_money_total = net_new_money_total + net_new_money
                            other_income_total = other_income_total +  other_income
                            
                            report_data.append([ific_code, contributer.code.upper(), fund.code.upper(), fund.type.name, fund.category.name, \
                                                fund.investment_type.name, 'Y' if fund.rrsp else 'N', sales_fee,'%s' % contributer.industry.name, \
                                                contributer.name, fund_name, '%.2f' % net_assets, '%.2f' % cash, '%.2f' % gross_sales, '%.2f' % reinvested_distribution, \
                                                '%.2f' % gross_redemptions, '%.2f' % transfers_in, '%.2f' % transfers_out, '%2f' % net_sales_inc,\
                                                '%.2f' % net_new_money, '%2f' % net_sales, unitholder, '%.2f' % capital_gains, '%.2f' % other_income, fund_index, fund_structure,])
                    except Exception as e:
                        pass
                        # warnings.append('Could not find fund %s for group %s in system' % (fund_code, contributer.code))
            
                index = index + 1
            
            #report_data.append(['', '%s Total' % contributer.code.upper(), '', '', '', '', '', '', '', '', '', '', '', '',\
            #                    '%.2f' % net_assets_total, '%.2f' % cash_total, '%.2f' % gross_sales_total, '%.2f' % reinvested_distribution_total,\
            #                    '%.2f' % gross_redemptions_total, '%.2f' % transfers_in_total, '%.2f' % transfers_out_total, '%.2f' % net_sales_total,\
            #                    '%.2f' % net_new_money_total, unitholder_total, '%.2f' % capital_gains_total, '%.2f' % other_income_total])
        else:
            file_pieces = file_path.split('/')
            warnings.append('%s/%s - Could not find uploaded template for company %s (%s)' % (file_pieces[-2], file_pieces[-1], contributer.name, contributer.code))
            
        
    
    if not os.path.isdir('%s/reports/' % settings.MEDIA_ROOT):
        try:
            
            os.mkdir('%s/reports/' % settings.MEDIA_ROOT)
        except:
            warnings.append('Could not create report directory')
                 
    report_file = '%s/reports/%s_stand_alone_view.csv' % (settings.MEDIA_ROOT, date)
    
    try:
        csv_writer = csv.writer(open(report_file, 'wb'), dialect=csv.excel_tab)
        
        for data in report_data:
            csv_writer.writerow([ x.encode('utf-8') if isinstance(x, unicode) else x for x in data ])
            
        response['status'] = 'ok'
    except Exception as e:
        warnings.append('Could not generate stand alone view')
    
    if len(warnings) > 0:
        response['warnings'] = warnings 
        
    if len(errors) > 0:
        response['status'] = 'error'
        response['errors'] = errors
    else:
        response['status'] = 'ok'
    
    data = { }
    data['complete_timestamp'] = datetime.now().strftime('%Y-%m-%d @ %H:%M')
    data['view'] = 'Stand Alone View'
    send_view_completed_email(data) 
    return response


@task
def generate_primary_investment_management_view(suppressed, estimated):
    warnings = []
    response = { }
    errors = []
    
    try:
        setting = UploadSetting.objects.get(pk=1)
        date = setting.upload_date.strftime('%Y-%m')
    except UploadSetting.DoesNotExist:
        errors.append('Upload date not defined')
    
    if suppressed == True:
        contributers = Contributer.objects.all()
    else:
        contributers = Contributer.objects.filter(hide=False)
        
    template_data = list()
    report_data = list()
    
    report_data = add_ific_header(report_data)
    for contributer in contributers:
        file_name = '%s_template1' % date
        file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, contributer.id, file_name)
        
        if os.path.isfile(file_path):
            with open(file_path, 'U') as csv_file:   
                template_data = list(csv.reader(csv_file, dialect='excel-tab'))        
         
            
            # Get Stand Alone Type
            stand_alone_investment_type = InvestmentType.objects.get(fund_of_fund=False)
            index = 0
            
             # Contributer Totals
            net_assets_total = 0.00
            cash_total = 0.00
            gross_sales_total = 0.00
            reinvested_distribution_total = 0.00
            gross_redemptions_total = 0.00
            transfers_in_total = 0.00
            transfers_out_total = 0.00
            net_sales_total = 0.00
            unitholder_total = 0
            capital_gains_total = 0.00
            net_new_money_total = 0.00
            other_income_total = 0.00
            
            for fund_code in template_data[1]:
                if len(fund_code) <= 3 and len(fund_code) > 0:
                    try:    
                        fund = Fund.objects.get(code__iexact=fund_code.lower(), contributer=contributer)
                        if (fund.investment_type.fund_of_fund == True and fund.investment_type.can_own_id == stand_alone_investment_type.id) or fund.investment_type.fund_of_fund == False: 
                            fund_data = get_column_data(template_data, index)
                                      
                            ific_code = '%s*%s' % (contributer.code.upper(), fund.code.upper())
                            fund_structure = fund.company_type.name
                            fund_classification = fund.classification.name
                            fund_index = 'Yes' if fund.index else 'No'
                            sales_fee = 0
                            fund_name = fund.name.replace(',', '')
                            
                            for s in Fund.SALES_FEE_CHOICES:
                                if s[0] == fund.sales_fee:
                                    sales_fee = s[1]
                                    break
                            
                            net_assets = float(fund_data[2].replace(',', '').replace('"', '').replace('$', ''))       
                            cash = float(fund_data[3].replace(',', '').replace('"', '').replace('$', ''))
                            gross_sales = float(fund_data[4].replace(',', '').replace('"', '').replace('$', ''))
                            reinvested_distribution = float(fund_data[5].replace(',', '').replace('"', '').replace('$', ''))
                            gross_redemptions = float(fund_data[6].replace(',', '').replace('"', '').replace('$', ''))
                            transfers_in = float(fund_data[7].replace(',', '').replace('"', '').replace('$', ''))
                            transfers_out = float(fund_data[8].replace(',', '').replace('"', '').replace('$', ''))
                            
                            unitholder = int(fund_data[10].replace(',', '').replace('"', '').replace('$', ''))
                            capital_gains = float(fund_data[11].replace(',', '').replace('"', '').replace('$', ''))
                            other_income = float(fund_data[12].replace(',', '').replace('"', '').replace('$', ''))
                                
                            found_it = False
                            for inner_c in contributers:
                                
                                template3_file_name = '%s_template3' % date
                                template3_file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, contributer.id, template3_file_name)
                                template3_data = { }
                                       
                                if os.path.isfile(template3_file_path):
                                    with open(template3_file_path, 'U') as csv_file:   
                                        template3_data = list(csv.reader(csv_file, dialect='excel-tab'))     

                                if len(template3_data) > 0:
                                    
                                    for data3 in template3_data:
                                        if len(data3) > 0:
                                            if len(data3[0]) <= 7:
                                                if data3[0].strip().find('*'):
                                                    split_code =  data3[0].strip().split('*')
                                                    # Make adjustments to values
                                                    if len(split_code) > 1:                                                        
                                                        if split_code[1].upper() == fund_code.upper() and split_code[0].upper() == contributer.code.upper() and found_it == False:
                                                            found_it = True
                                                                                                                            
                                                            net_assets = net_assets - float(data3[2].replace(',', '').replace('"', '').replace('$', ''))
                                                            gross_sales = gross_sales - float(data3[3].replace(',', '').replace('"', '').replace('$', ''))
                                                            gross_redemptions = gross_redemptions - float(data3[4].replace(',', '').replace('"', '').replace('$', ''))
                                                            transfers_in = transfers_in - float(data3[5].replace(',', '').replace('"', '').replace('$', ''))
                                                            transfers_out = transfers_out - float(data3[6].replace(',', '').replace('"', '').replace('$', ''))
                                                            
                            if fund.investment_type.id == 1 or fund.investment_type.id == 2:                              
                                net_sales = gross_sales - gross_redemptions + transfers_in - transfers_out
                                net_new_money = gross_sales - gross_redemptions
                                net_sales_inc = gross_sales + reinvested_distribution - gross_redemptions + transfers_in - transfers_out
                                #net_assets_total = net_assets_total + net_assets
                                #cash_total = cash_total + cash
                                #gross_sales_total = gross_sales_total + gross_sales
                                #reinvested_distribution_total = reinvested_distribution_total + reinvested_distribution
                                #gross_redemptions_total = gross_redemptions_total + gross_redemptions
                                #transfers_in_total = transfers_in_total + transfers_in
                                #transfers_out_total = transfers_out_total + transfers_out
                                #net_sales_total = net_sales_total + net_sales
                                #net_new_money_total = net_new_money_total + net_new_money
                                #unitholder_total = unitholder_total + unitholder
                                #capital_gains_total = capital_gains_total + capital_gains
                                #other_income_total = other_income_total + other_income
                                    
                                        
                                report_data.append([ific_code, contributer.code.upper(), fund.code.upper(), fund.type.name, fund.category.name, \
                                                    fund.investment_type.name, 'Y' if fund.rrsp else 'N', sales_fee, '%s' % contributer.industry.name, \
                                                    contributer.name, fund_name,'%.2f' % net_assets, '%.2f' % cash, '%.2f' % gross_sales, '%.2f' % reinvested_distribution, \
                                                    '%.2f' % gross_redemptions, '%.2f' % transfers_in, '%.2f' % transfers_out, '%.2f' % net_sales_inc, \
                                                    '%.2f' % net_new_money, '%2f' % net_sales, unitholder, '%.2f' % capital_gains, '%.2f' % other_income,  fund_index, fund_structure])
                    except Fund.DoesNotExist:
                        pass
                        #warnings.append('Fund %s for Group %s does not exist in system' % (fund_code, contributer.code.upper()))
                        
                index = index + 1
                            
            #report_data.append(['', '%s Total' % contributer.code.upper(), '', '', '', '', '', '', '', '', '', '', '', '',\
            #                    '%.2f' % net_assets_total, '%.2f' % cash_total, '%.2f' % gross_sales_total, '%.2f' % reinvested_distribution_total,\
            #                    '%.2f' % gross_redemptions_total, '%.2f' % transfers_in_total, '%.2f' % transfers_out_total, '%.2f' % net_sales_total,\
            #                    '%.2f' % net_new_money_total, unitholder_total, '%.2f' % capital_gains_total, '%.2f' % other_income_total])    
        else:
            file_pieces = file_path.split('/')
            warnings.append('%s/%s - Could not find uploaded template for company %s (%s)' % (file_pieces[-2], file_pieces[-1], contributer.name, contributer.code))
     
    
    if not os.path.isdir('%s/reports/' % settings.MEDIA_ROOT):
        try:
            os.mkdir('%s/reports/' % settings.MEDIA_ROOT)
        except:
            warnings.append('Could not create report directory')
    
             
    report_file = '%s/reports/%s_primary_investment_management.csv' % (settings.MEDIA_ROOT, date)
    
    try:
        csv_writer = csv.writer(open(report_file, 'wb'), dialect=csv.excel_tab)
        
        for data in report_data:
            csv_writer.writerow([ x.encode('utf-8') if isinstance(x, unicode) else x for x in data ])
            
        response['status'] = 'ok'
    except Exception as e:
        warnings.append('Primary Investment Management View')
    
    if len(warnings) > 0:
        response['status'] = 'warnings'
        response['warnings'] = warnings   
    
    data = { }
    data['complete_timestamp'] = datetime.now().strftime('%Y-%m-%d @ %H:%M')
    data['view'] = 'Primary Investment Management View'
    send_view_completed_email(data) 
    
    return response

@task
def generate_funds_administration_view(suppressed, estimated):
    warnings = []
    response = { }
    errors = []
  
    try:
        setting = UploadSetting.objects.get(pk=1)
        date = setting.upload_date.strftime('%Y-%m')
    except UploadSetting.DoesNotExist:
        errors.append('Upload date not defined')
    
    if suppressed == True:
        contributers = Contributer.objects.all()
    else:
        contributers = Contributer.objects.filter(hide=False)
        
    template_data = list()
    report_data = list()
    
    report_data = add_ific_header(report_data)    
    for contributer in contributers:
        file_name = '%s_template1' % date
        file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, contributer.id, file_name)
        
        if os.path.isfile(file_path):
            with open(file_path, 'U') as csv_file:   
                template_data = list(csv.reader(csv_file, dialect='excel-tab'))        
             
           
                 
            # Get Stand Alone Type
            stand_alone_investment_type = InvestmentType.objects.get(fund_of_fund=False)
            index = 0
            
             # Contributer Totals
            net_assets_total = 0.00
            cash_total = 0.00
            gross_sales_total = 0.00
            reinvested_distribution_total = 0.00
            gross_redemptions_total = 0.00
            transfers_in_total = 0.00
            transfers_out_total = 0.00
            net_sales_total = 0.00
            unitholder_total = 0
            capital_gains_total = 0.00
            net_new_money_total = 0.00
            other_income_total = 0.00
            
            for fund_code in template_data[1]:
                fund_data = get_column_data(template_data, index)

                if len(fund_code) <= 3 and len(fund_code) > 0:

                    try:
                        fund = Fund.objects.get(code=fund_code, contributer=contributer)
                        ific_code = '%s*%s' % (contributer.code.upper(), fund.code.upper())
                        fund_structure = fund.company_type.name
                        fund_classification = fund.classification.name
                        fund_index = 'Yes' if fund.index else 'No'
                        fund_name = fund.name.replace(',', '')
                        sales_fee = 0

                        for s in Fund.SALES_FEE_CHOICES:
                            if s[0] == fund.sales_fee:
                                sales_fee = s[1]
                                break
                        
                        net_assets = float(fund_data[2].replace(',', '').replace('"', '').replace('$', ''))       
                        cash = float(fund_data[3].replace(',', '').replace('"', '').replace('$', ''))
                        gross_sales = float(fund_data[4].replace(',', '').replace('"', '').replace('$', ''))
                        reinvested_distribution = float(fund_data[5].replace(',', '').replace('"', '').replace('$', ''))
                        gross_redemptions = float(fund_data[6].replace(',', '').replace('"', '').replace('$', ''))
                        transfers_in = float(fund_data[7].replace(',', '').replace('"', '').replace('$', ''))
                        transfers_out = float(fund_data[8].replace(',', '').replace('"', '').replace('$', ''))
                        unitholder = int(fund_data[10].replace(',', '').replace('"', '').replace('$', ''))
                        capital_gains = float(fund_data[11].replace(',', '').replace('"', '').replace('$', ''))
                        other_income = float(fund_data[12].replace(',', '').replace('"', '').replace('$', ''))
                        
                        
                        
                        
                        if fund.investment_type.fund_of_fund == False:
                            
                            for inner_c in contributers:
                                template2_file_name = '%s_template2' % date
                                template2_file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, inner_c.id, template2_file_name)
                                template2_data = { }
                                template3_file_name = '%s_template3' % date
                                template3_file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, inner_c.id, template3_file_name)
                                
                                if os.path.isfile(template2_file_path):
                                    with open(template2_file_path, 'U') as csv_file:   
                                        template2_data = list(csv.reader(csv_file, dialect='excel-tab'))     
                                else:
                                    if os.path.isfile(template3_file_path):
                                        with open(template3_file_path, 'U') as csv_file:   
                                            template2_data = list(csv.reader(csv_file, dialect='excel-tab'))   
                                    else:
                                        pass
                                        
                                        
                                if len(template2_data) > 0:
                                        for data2 in template2_data:
                                            if len(data2) > 0:
                                                if len(data2[0]) <= 7:
                                                    if data2[0].strip().find('*'):
                                                        split_code =  data2[0].strip().split('*')
                                                        
                                                        if len(split_code) > 1:
                                                            # Make adjustments to values
                                                            
                                                            if split_code[1].upper() == fund_code.upper() and split_code[0].upper() == contributer.code.upper():
                                                                net_assets = net_assets - float(data2[2].replace(',', '').replace('"', '').replace('$', ''))
                                                                gross_sales = gross_sales - float(data2[3].replace(',', '').replace('"', '').replace('$', ''))
                                                                gross_redemptions = gross_redemptions - float(data2[4].replace(',', '').replace('"', '').replace('$', ''))
                                                                transfers_in = transfers_in - float(data2[5].replace(',', '').replace('"', '').replace('$', ''))
                                                                transfers_out = transfers_out - float(data2[6].replace(',', '').replace('"', '').replace('$', ''))
                            
                        
                        net_sales = gross_sales - gross_redemptions + transfers_in - transfers_out
                        net_sales_inc = gross_sales + reinvested_distribution - gross_redemptions + transfers_in - transfers_out
                        net_new_money = gross_sales - gross_redemptions
                        
                        net_assets_total = net_assets_total + net_assets
                        cash_total = cash_total + cash
                        gross_sales_total = gross_sales_total + gross_sales
                        reinvested_distribution_total = reinvested_distribution_total + reinvested_distribution
                        gross_redemptions_total = gross_redemptions_total + gross_redemptions
                        transfers_in_total = transfers_in_total + transfers_in
                        transfers_out_total = transfers_out_total + transfers_out
                        net_sales_total = net_sales_total + net_sales
                        unitholder_total = unitholder_total + unitholder
                        capital_gains_total = capital_gains_total + capital_gains
                        net_new_money_total = net_new_money_total + net_new_money
                        other_income_total = other_income_total + other_income
                        
                        report_data.append([ific_code, contributer.code.upper(), fund.code.upper(), fund.type.name, fund.category.name, \
                                            fund.investment_type.name, 'Y' if fund.rrsp else 'N', sales_fee, '%s' % contributer.industry.name, \
                                            contributer.name, fund_name,'%.2f' % net_assets, '%.2f' % cash, '%.2f' % gross_sales, '%.2f' % reinvested_distribution, \
                                            '%.2f' % gross_redemptions, '%.2f' % transfers_in, '%.2f' % transfers_out, '%2f' % net_sales_inc, \
                                            '%.2f' % net_new_money, '%2f' % net_sales, unitholder, '%.2f' % capital_gains, '%.2f' % other_income,  fund_index, fund_structure])     
                           
                    except Fund.DoesNotExist:
                        pass
                        #warnings.append('Fund %s does not exist in system' % (fund_code))
                         
                index = index + 1
                            
            #report_data.append(['', '%s Total' % contributer.code.upper(), '', '', '', '', '', '', '', '', '', '', '', '', \
            #                    '%.2f' % net_assets_total, '%.2f' % cash_total, '%.2f' % gross_sales_total, '%.2f' % reinvested_distribution_total,\
            #                    '%.2f' % gross_redemptions_total, '%.2f' % transfers_in_total, '%.2f' % transfers_out_total, '%.2f' % net_sales_total,\
            #                    '%.2f' % net_new_money_total, unitholder_total, '%.2f' % capital_gains_total, '%.2f' % other_income_total])
        else:
            warnings.append('File (template 1) does not exist for group %s' % contributer.code)

    if not os.path.isdir('%s/reports/' % settings.MEDIA_ROOT):
        try:
            os.mkdir('%s/reports/' % settings.MEDIA_ROOT)
        except:
            warnings.append('Could not create report directory')
       
    report_file = '%s/reports/%s_funds_administration_view.csv' % (settings.MEDIA_ROOT, date)

    try:
        csv_writer = csv.writer(open(report_file, 'wb'), dialect=csv.excel_tab)
        
        for data in report_data:
            csv_writer.writerow([ x.encode('utf-8') if isinstance(x, unicode) else x for x in data ])
            
        response['status'] = 'ok'
    except Exception as e:
        warnings.append('Could not generate Funds Administration View')
    
    if len(warnings) > 0:
        response['warnings'] = warnings 
        
    if len(errors) > 0:
        response['status'] = 'error'
        response['errors'] = errors
    else:
        response['status'] = 'ok'
        
    data = { }
    data['complete_timestamp'] = datetime.now().strftime('%Y-%m-%d @ %H:%M')
    data['view'] = 'Funds Administration View'
    
    send_view_completed_email(data)             
    return response


@login_required
def get_standalone_result(request):

    response = { }
    if 'stand_alone_view_response' in request.session:
        stand_alone_response = request.session['stand_alone_view_response']
        if stand_alone_response.result:
            response['sa_response'] = stand_alone_response.result
        else:
            pass
    else:
        response['sa_response'] = []
    
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')


@login_required
def get_primary_investment_result(request):
    response = { }
    if 'primary_investment_response' in request.session:
        primary_investment_response = request.session['primary_investment_response']
        if primary_investment_response.result:
            response['pim_response'] = primary_investment_response.result
        else:
            pass
    else:
        response['pim_response'] = []
    
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')

@login_required
def get_funds_admin_result(request):
    response = { }
    if 'funds_admin_response' in request.session:
        funds_admin_response = request.session['funds_admin_response']
        if funds_admin_response.result:
            response['av_response'] = funds_admin_response.result
        else:
            pass
    else:
        response['av_response'] = []
    
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')


@login_required
def ajax_clear_result(request):
    response = { }
    
    if 'view' in request.GET:
        if request.GET['view'] == 'standalone':
            if 'stand_alone_view_response' in request.session:
                try:
                    del request.session['stand_alone_view_response']
                    
                except KeyError:
                    pass
            else:
                pass
        if request.GET['view'] == 'primary-investment':
            if 'primary_investment_response' in request.session:
                try:
                    del request.session['primary_investment_response']
                except KeyError:
                    pass
            else:
                pass
        if request.GET['view'] == 'funds-admin':
            if 'funds_admin_response' in request.session:
                try:
                    del request.session['funds_admin_response']
                except KeyError:
                    pass
            else:
                pass   
            
        response['status'] = 'ok'     
    else:
        response['status'] = 'ok' 
    
    
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')

@login_required
def ajax_aggregate(request):
    response = { }
    errors = []
    
    user = request.user
    try:
        allowed = check_user_permissions(user, ['admin'])
    except Exception as e:
        errors.append(e.msg)
    
    suppressed = False
    if 'suppressed' in request.GET:
        if int(request.GET['suppressed']) == 1:
            suppressed = True
    estimated = False
    
    if 'estimated' in request.GET:
        if int(request.GET['estimated']) == 1:
            estimated = True

    sa_response = []
    pim_response = []
    av_response = []
    
    if 'type' in request.GET:
        if allowed:
            # @TODO: Run checks to make sure that everything has been validated
            if int(request.GET['type']) == 1:
                task_response = generate_standalone_view.delay(suppressed, estimated)
                request.session['stand_alone_view_response'] = task_response
                
            if int(request.GET['type']) == 2:
                task_response = generate_primary_investment_management_view.delay(suppressed, estimated)
                request.session['primary_investment_response'] = task_response
                
            if int(request.GET['type']) == 3:
                task_response = generate_funds_administration_view.delay(suppressed, estimated)
                request.session['funds_admin_response'] = task_response
                
                
                
    response['sa_response'] = sa_response
    response['pim_response'] = pim_response
    response['av_response'] = av_response
            
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')
    
@login_required
def ajax_add_contributer(request):
    response = { }
    errors = []
    
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        errors.append('No user profile')
        
    try:
        allowed = check_user_permissions(user, ['contributer', 'admin'])
    except Exception as e:
        errors.append(e.msg)
    
    if allowed:
        contributer = Contributer()
        
        if 'name' in request.GET:
            try:
                Contributer.objects.get(name=request.GET['name'])
                errors.append('This company name already exists')
            except Contributer.DoesNotExist:
                contributer.name = request.GET['name']
        else:
            errors.append('Please provide a company name')
            
        if 'code' in request.GET:
            try:
                Contributer.objects.get(code=request.GET['code'].lower())
                errors.append('Company code already exists')
            except Contributer.DoesNotExist:
                contributer.code = request.GET['code'].lower()
        else:
            errors.append('Please provide a unique company code')
        
        if profile.user_type.type == 'admin':    
            if 'hide' in request.GET:
                if int(request.GET['hide']) == 1:
                    contributer.hide = True
                else:
                    contributer.hide = False
    
        if 'status' in request.GET:
            if int(request.GET['status']) == 1:
                contributer.stats = True
            else:
                contributer.status = False
                
        if 'industry' in request.GET:
            try:
                industry = Industry.objects.get(pk=int(request.GET['industry']))
                contributer.industry = industry
            except Industry.DoesNotExist:
                errors.append('This industry does not exist')        


        # Creating a new user
        elif 'username' in request.GET:
            if 'password' not in request.GET:
                errors.append('Pease provide a password')
            
            if 'password_confirm' not in request.GET:
                errors.append('Please confirm the password')
                
            if 'email' not in request.GET:
                errors.append('Please provide a user email')
                
        
        if len(errors) == 0:
            try:                
                contributer.save()
                if 'users[]' in request.GET:
                    user_list = request.GET.getlist('users[]')
                    for ul in user_list:
                        try:
                            u = User.objects.get(pk=int(ul))
                            if u not in contributer.users.all():
                                contributer.users.add(u)
                        except User.DoesNotExist:
                            errors.append('User %d does not exist' % ul)
                        
                AllowedTemplate.objects.filter(contributer=contributer, template_type=2).delete()

                
                if 'allowed_template2[]' in request.GET:
                    fund_list = request.GET.getlist('allowed_template2[]')
                    for fund_id in fund_list:
                        try:
                            fund = Fund.objects.get(pk=int(fund_id))
                            allowed_template2 = AllowedTemplate(contributer=contributer)
                            allowed_template2.template_type = 2
                            allowed_template2.fund = fund
                            allowed_template2.save()
                        except Fund.DoesNotExist:
                            errors.append('Fund %d does not exist' % fund_id)
                            
                AllowedTemplate.objects.filter(contributer=contributer, template_type=3).delete()
                if 'allowed_template3[]' in request.GET:
                    fund_list = []
                    fund_list = request.GET.getlist('allowed_template3[]')
                    for fund_id in fund_list:
                        try:
                            fund = Fund.objects.get(pk=int(fund_id))
                            allowed_template3 = AllowedTemplate(contributer=contributer)
                            allowed_template3.template_type = 3
                            allowed_template3.fund = fund
                            allowed_template3.save()
                        except Fund.DoesNotExist:
                            errors.append('Fund %d does not exist' % fund_id)                    
                    
                response['status'] = 'ok'
                response['message'] = 'Company Added'
            except Exception as e:
                errors.append(e)
                response['status'] = 'error'
                response['message'] = 'An error has occured'
                response['errors'] = errors
        else:
            response['status'] = 'error'
            response['message'] = 'Errors have occured'
            response['errors'] = errors
    else:
        response['status'] = 'error'
        response['message'] = 'Invalid permissions'
        
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')      
    
        
# Check if company code exists in database

@login_required
def ajax_check_contributer_code(request):
    response = { }
    user = request.user

    try:
        allowed = check_user_permissions(user, ['contributer', 'admin'])
    except Exception as e:
        errors.append(e.msg)
        
    if allowed:
        if 'code' in request.GET:
            code = request.GET['code'].lower()
            try:
                
                if len(code) <= 3:
                    contributer = Contributer.objects.get(code=code)
                    response['status'] = 'error'
                    response['message'] = 'This code already exists in the system'
                else:
                    response['status'] = 'error'
                    response['message'] = 'Invalid code provided'
                    
            except Contributer.DoesNotExist:
                response['status'] = 'ok'
                
        else:
            response['status'] = 'error'
            response['message'] = 'No code provided'
    else:
        response['status'] = 'error'
        response['message'] = 'Invalid permissions'
            
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')

@login_required
def ajax_check_fund_code(request):
    response = { }
    errors = []
    
    user = request.user

    try:
        allowed = check_user_permissions(user, ['contributer', 'admin'])
    except Exception as e:
        errors.append(e.msg)
        
    if allowed:  
        if 'code' in request.GET:
            code = request.GET['code'].lower()
            try:
                
                if len(code) <= 3:
                    contributer = Fund.objects.get(code=code)
                    response['status'] = 'error'
                    response['message'] = 'This code already exists in the system'
                else:
                    response['status'] = 'error'
                    response['message'] = 'Invalid code provided'
                    
            except Fund.DoesNotExist:
                response['status'] = 'ok'
    else:
        response['status'] = 'error'
        response['message'] = 'Invalid permissions'
            
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')

@login_required
def ajax_complete(request):
    response = { }
    
    try:
        if 'step' in request.session:
            print request.session['step']
            request.session['step'] = 0
            try:
                if 'contributer' in request.session:
                    del request.session['contributer']
            except:
                pass
    except:
        pass
    
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')

@login_required
def ajax_delete_contributer(request):
    response = { }
    errors = []
    
    user = request.user
    try:
        allowed = check_user_permissions(user, ['admin'])
    except Exception as e:
        errors.append(e.msg)
    
    if allowed:
        if 'id' in request.GET:
            try:
                if id:
                    contributer = Contributer.objects.get(pk=int(request.GET['id']))
                else:
                    errors.append('Invalid company id')
            except Contributer.DoesNotExist:
                errors.append('Company does not exist')
    else:
        errors.append('Invalid permissions')
    
    if len(errors) == 0:
         contributer.users.clear()
         contributer.delete()
         response['status'] = 'ok'
    else:
        response['status'] = 'error'
        response['message'] = 'Errors have occured'
        response['errors'] = errors
        
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')    
    
   
# Edit Contributer    

@login_required
def ajax_edit_contributer(request):
    response = { }
    errors = []
    
    user = request.user
    
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        errors.append('No user profile')
        
    try:
        allowed = check_user_permissions(user, ['admin'])
    except Exception as e:
        errors.append(e.msg)
    
    if allowed:
        if 'id' in request.GET:
            try:
                if id:
                    contributer = Contributer.objects.get(pk=int(request.GET['id']))
                    
                    if 'name' in request.GET:
                        if len(request.GET['name']) > 0:
                            contributer.name = request.GET['name']
                        else:
                            errors.append('Invalid company name')
                    else:
                        errors.append('Please provide a company name')
                    
                    
                    if profile.user_type.type == 'admin':    
                         if 'hide' in request.GET:
                            if int(request.GET['hide']) == 1:
                                 contributer.hide = True
                            else:
                                contributer.hide = False
                      
                    if 'status' in request.GET:
                        if int(request.GET['status']) == 1:
                            contributer.active = True
                        else:
                            contributer.active = False
                    
                    if 'industry' in request.GET:
                        try:
                            industry = Industry.objects.get(pk=int(request.GET['industry']))
                            contributer.industry = industry
                        except Industry.DoesNotExist:
                            errors.append('Invalid industry provided')
                    else:
                        errors.append('Please provide an industry')
                        
                    if 'users[]' in request.GET:
                        user_list = request.GET.getlist('users[]')
                        contributer.users.clear()
                        for ul in user_list:
                            try:
                                u = User.objects.get(pk=int(ul))
                                if u not in contributer.users.all():
                                    contributer.users.add(u)
                            except User.DoesNotExist:
                                errors.append('User %d does not exist', ul)
                                
                    AllowedTemplate.objects.filter(contributer=contributer, template_type=2).delete()
                    if 'allowed_template2[]' in request.GET:
                        fund_list = request.GET.getlist('allowed_template2[]')
                        for fund_id in fund_list:
                            try:
                                fund = Fund.objects.get(pk=int(fund_id))
                                allowed_template2 = AllowedTemplate(contributer=contributer)
                                allowed_template2.template_type = 2
                                allowed_template2.fund = fund
                                allowed_template2.save()
                            except Fund.DoesNotExist:
                                errors.append('Fund %d does not exist' % fund_id)
                    
                    AllowedTemplate.objects.filter(contributer=contributer, template_type=3).delete()
                    if 'allowed_template3[]' in request.GET:
                        fund_list = []
                        fund_list = request.GET.getlist('allowed_template3[]')
                        for fund_id in fund_list:
                            try:
                                fund = Fund.objects.get(pk=int(fund_id))
                                allowed_template3 = AllowedTemplate(contributer=contributer)
                                allowed_template3.template_type = 3
                                allowed_template3.fund = fund
                                allowed_template3.save()
                            except Fund.DoesNotExist:
                                errors.append('Fund %d does not exist' % fund_id)   
                else:
                    errors.append('Invalid ID')
                      
            except Contributer.DoesNotExist:
                errors.append('Group does not exist')
                
            if len(errors) == 0:
                try:
                    contributer.save()
                    response['status'] = 'ok'
                except Exception as e:
                    response['status'] = 'error'
                    response['message'] = e
            else:
                response['status'] = 'error'
                response['message'] = 'Errors have occured'
                response['errors'] = errors
        else:
            response['status'] = 'error'
            response['message'] = 'Please provide a company to edit'
    else:
        response['status'] = 'error'
        response['message'] = 'Invalid permissions'
        
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')   

@login_required
def ajax_find_contributer(request):
    response = ''
    errors = []
    
    user = request.user
        
    try:
        allowed = check_user_permissions(user, ['admin', 'contributer'])
    except Exception as e:
        allowed = False
        response = ''
    if allowed:
        if 'q' in request.GET:
            try:
                user_profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                response = ''
            
            if user_profile.user_type.type == 'admin':
                contributers = Contributer.objects.filter(name__icontains=request.GET['q'])[:10]
            elif user_profile.user_type.type == 'contributer': 
                contributers = Contributer.objects.filter(name__icontains=request.GET['q'], users__in=[user])[:10]
            else:
                contributers = []
            
                    
                   
            response = [(x.name, x.id, x.code) for x in contributers]
    else:
        response = ''
        
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')
    
@login_required
def ajax_find_fund(request):
    response = ''
    errors = []
    
    user = request.user
    
    try:
        allowed = check_user_permissions(user, ['admin'])
    except Exception as e:
        allowed = False
        response = ''
    if allowed:
        if 'q' in request.GET:
            if 'type' in request.GET:
                
                try:
                    investment_type = InvestmentType.objects.get(pk=int(request.GET['type']))
                    
                except InvestmentType.DoesNotExist:
                    response = 'Invalid investment type' 
                    
                if investment_type.fund_of_fund == True:
                    if 'contributer' in request.GET:
                        
                        if investment_type.company == InvestmentType.NONE:
                            response = 'Invalid query cannot own funds of funds'
                        
                        if investment_type.company == InvestmentType.SELF:
                            funds = Fund.objects.filter(name__icontains=request.GET['q'], investment_type=investment_type.can_own, contributer=int(request.GET['contributer']))[:10]
                        
                        if investment_type.company == InvestmentType.OTHER:
                            funds = Fund.objects.filter(name__icontains=request.GET['q'], investment_type=investment_type.can_own).exclude(contributer = int(request.GET['contributer']))[:10]
                        
                        if investment_type.company == InvestmentType.ANY:
                            funds = Fund.objects.filter(name__icontains=request.GET['q'], investment_type=investment_type.can_own)[:10]
                        
                    else:
                        response = 'No contributer provided'
                else:

                    funds = []  
                
            else:
                funds = Fund.objects.filter(name__icontains=request.GET['q'])[:10]
            response = [(x.name, x.id, x.code, x.investment_type.name, x.investment_type.id, '%s*%s' % (x.contributer.code.upper(), x.code.upper())) for x in funds]
    else:
        response = ''
                 
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')    

@login_required
def ajax_find_transaction(request):
    response = ''
    user = request.user
    try:
        allowed = check_user_permissions(user, ['admin'])
    except Exception as e:
        allowed = False
    
    transactions = []
    
    if allowed:
        if 'q' in request.GET:
            try:
                transactions = Transaction.objects.filter(id=int(request.GET['q']))
            except Transaction.DoesNotExist:
                transactions = []
            
            response = [(x.id) for x in transactions]
    else:
        response = ''
    
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')   

@login_required
def ajax_find_user(request):
    response = ''
    
    user = request.user
    
    try:
        allowed = check_user_permissions(user, ['admin'])
    except Exception as e:
        allowed = False
    
    users = []
    if allowed:
        if 'q' in request.GET:
            try:
                users = User.objects.filter(username__icontains=request.GET['q'])
            except User.DoesNotExist:
                users = []
                
    
        response = [(x.username, x.id) for x in users]
    
    
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')
    

# Login functions
@csrf_exempt
def ajax_login(request):

    response = { }
    errors = []
    if 'user' in request.POST:
        try:
            if 'password' in request.POST:
                user = authenticate(username=request.POST['user'], password=request.POST['password'])
                if user != None:
                    auth_login(request, user)
                    try:
                        user_profile = UserProfile.objects.get(user=user)
                        user_type = user_profile.user_type
                        
                        user_log = UserLog(user=user) 
                        if 'HTTP_X_FORWARDED_FOR' in request.META:
                            user_log.ip_address = request.META['HTTP_X_FORWARDED_FOR']
                        else:
                            if 'REMOTE_ADDR' in request.META:
                                user_log.ip_address = request.META['REMOTE_ADDR']

                        if len(user_log.ip_address) > UserLog._meta.get_field('ip_address').max_length:
                            user_log.ip_address = user_log.ip_address[:UserLog._meta.get_field('ip_address').max_length]
                                
                        user_log.save()
                        
                        if user_type.type == 'contributer':
                            response['redirect'] = '/admin/statistics'
 
                        if user_type.type == 'subscriber':
                            response['redirect'] = '/admin/statistics'
                            
                        if user_type.type == 'customer':
                            response['redirect'] = '/admin/statistics'
                        
                        if user_type.type == 'admin':
                            response['redirect'] = '/admin/groups'
                        
                        
                        if 'HTTP_X_FORWARDED_FOR' in request.META:
                            user_profile.ip_address = request.META['HTTP_X_FORWARDED_FOR']
                        else:
                            if 'REMOTE_ADDR' in request.META:
                                user_profile.ip_address = request.META['REMOTE_ADDR']
                        
                        if len(user_profile.ip_address) > UserProfile._meta.get_field('ip_address').max_length:
                            user_profile.ip_address = user_profile.ip_address[:UserProfile._meta.get_field('ip_address').max_length]
                        
                        user_profile.save()
                        response['status'] = 'ok'
                        
                    except UserProfile.DoesNotExist:
                        errors.append('User profile not created')
                else:
                    errors.append('Invalid credentials')
            else:
                errors.append('Please provide a password')
        except Exception as e:
            errors.append('%s' % e)
    else:
        errors.append('Please provide a user name')
        

    
    if len(errors) == 0:
        response['status'] = 'ok'    
    else:
        response['status'] = 'error'
        response['message'] = 'Errors have occured'
        response['errors'] = errors
        
    
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')   

@login_required
def ajax_purchase(request):
    response = { }
    errors = []
    user = request.user
    template_data = { }
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        errors.append('Profile does not exist')
    
    current_date = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':

        purchase_packages = []
        if 'packageCount' in request.POST:
            package_count = int(request.POST['packageCount'])
            
            for x in range(0, package_count):
                key = 'packages[%s][]' % x
                package_data = request.POST.getlist(key)
                purchase_packages.append(package_data)
        
        if 'address' in request.POST and len(request.POST['address']) > 0:
            template_data['address'] = request.POST['address']
        else:
            errors.append('Invalid address provided')
        
        if 'city' in request.POST and len(request.POST['city']) > 0:
            template_data['city'] = request.POST['city']
        else:
            errors.append('Invalid city provided')
        
        if 'state' in request.POST and len(request.POST['state']) == 2:
            template_data['state'] = request.POST['state']
        else:
            errors.append('Invalid state/province provided')
            
        if 'country' in request.POST and len(request.POST['country']) == 2:
            template_data['country'] = request.POST['country']
        else:
            errors.append('Invalid country provided')
        
        if 'zip' in request.POST and len(request.POST['zip']) >= 5:
            template_data['zip'] = request.POST['zip']
        else:
            errors.append('Invalid zip/postal code')
        
        
        if 'payment_type' in request.POST:
            if request.POST['payment_type'] == 'credit_card': 
                
                if 'name' in request.POST and len(request.POST['name']) > 0:
                    template_data['name'] = request.POST['name']
                else:
                    errors.append('Invalid cardholder name provided')
                               
                if 'credit_card' in request.POST and (len(request.POST['credit_card']) > 12 and len(request.POST['credit_card']) < 20):
                    template_data['credit'] = request.POST['credit_card']
                else:
                    errors.append('Invalid credit card')
                
                if 'ccv' in request.POST and len(request.POST['ccv']) == 3:
                    template_data['cvv'] = request.POST['ccv']
                else:
                    errors.append('Invalid ccv')
                    
                if 'month' in request.POST and len(request.POST['month']) == 2:
                    template_data['month'] = request.POST['month']
                else:
                    errors.append('Invalid expire month')
                    
                if 'year' in request.POST and len(request.POST['year']) == 4:
                    now = datetime.now()
        
                    if int(request.POST['year']) >= now.year: 
                        template_data['year'] = request.POST['year']
                    else:
                        errors.append('Invalid year')
                else:
                    errors.append('Invalid year')
        else:
            errors.append('Please select payment type')
            
        date_check = timedelta(weeks=2)
        new_packages = []
        update_transactions = []
        price = 0.00
        
        for p in purchase_packages:
            try:
                package_check = Package.objects.get(id=int(p[1]))
                user_transaction = Transaction.objects.get(user=user, expires__gt=current_date, package=package_check)
                
                if int(p[3]) == 1:
                    price = price + package_check.price
                else:
                    price = price + package_check.per_file_price
                    
                if user_transaction.expires - date.today() <= date_check:
                    update_transactions.append(user_transaction)
                else:
                    errors.append('You have already purchased this package')
                    
            except Package.DoesNotExist:
                errors.append('Package %d does not exist' % int(p[1]))
            except Transaction.DoesNotExist:
                if int(p[3]) == 1:
                    price = price + package_check.price
                else:
                    price = price + package_check.per_file_price
                    
                new_packages.append(package_check)
             
              
        # Send Purcahse to Internet Secure
        if len(errors) == 0:
            
            if request.POST['payment_type'] == 'credit_card':
                # Add HST
                price = float(price) * 1.13
                
                template_data['price'] = float(price)
                template_data['gateway'] = GATEWAY
                
                post_data = { }
                payment_xml = render_to_string('internetsecure.xml', template_data, context_instance=RequestContext(request))
                
                post_data['xxxRequestMode'] = 'X'
                post_data['xxxRequestData'] =  payment_xml
                post_data = urllib.urlencode(post_data)
                
                try:
                    request = urllib2.Request(GATEWAY_URL, post_data)
                    http_response = urllib2.urlopen(request)
                    xml_response = http_response.read()
                    
                    dom = parseString(xml_response)
                    receipt = dom.getElementsByTagName('ReceiptNumber')
                    ip_address = dom.getElementsByTagName('xxxCustomerIP')
                    transaction_date = dom.getElementsByTagName('Date')
                    page_code = dom.getElementsByTagName('Page')
                    
    
                    
                except Exception as e:
                    errors.append('Could not process transaction at this time')

                new_price = 0.00
                if int(page_code[0].firstChild.data) == 2000 or int(page_code[0].firstChild.data) == 90000:
                    new_transactions = []
                    try:    
                        for p in purchase_packages:
                            try:
                                package = Package.objects.get(pk=int(p[1]))
                                if package in new_packages:
                                    new_transaction = Transaction(user=user)
                                    new_transaction.package = package
                                    if int(p[3]) == 1:
                                        new_transaction.expires = date.today() + timedelta(days=365)
                                        new_transaction.price = package.price
                                    if int(p[3]) == 2:
                                        new_transaction.expires = date.today() + timedelta(days=91)
                                        new_transaction.price = package.per_file_price
                                    if int(p[3]) == 3:
                                        new_transaction.expires = date.today() + timedelta(days=30)
                                        new_transaction.price = package.per_file_price
                                    
                                    new_transaction.page_code = page_code
                                    new_transaction.receipt_number = receipt[0].firstChild.data
                                    new_transaction.type =  Transaction.CREDIT_CARD
                                    new_transaction.valid = True
                                    new_transaction.save()
                                    new_transactions.append(new_transaction)
                                    
                                for t in update_transactions:
                                    if t.package == package:
                                        if int(p[3]) == 1:
                                            t.expires = t.expires + timedelta(days=365)
                                            t.price = package.price
                                        if int(p[3]) == 2:
                                            t.expires = t.expires + timedelta(days=91)
                                            t.price = package.per_file_price
                                        if int(p[3]) == 3:
                                            t.expires = t.expires + timedelta(days=30)
                                            t.price = package.per_file_price
                                        
                                        t.valid = True
                                        t.save()
                                    
                            except Package.DoesNotExist:
                                errors.append('Package does not exist')
    
                        email_data = { }
                        email_data['update_transactions'] = update_transactions
                        email_data['new_transactions'] = new_transactions
                        email_data['user'] = user
                        email_data['profile'] = profile
                        email_data['payment_type'] = 'Credit'
                        email_data['address'] =  template_data['address']
                        email_data['city'] = template_data['city'] 
                        email_data['country'] = template_data['country'] 
                        email_data['state'] = template_data['state']
                        email_data['zip'] = template_data['zip']
                        email_data['timestamp'] =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        
                        send_email(['statistics@ific.ca', user.email], 'noreply@ific.ca', email_data, 'cheque_email.html', 'IFIC Package Purchase')

            
                        response['redirect'] = '/admin/statistics'
                        response['status'] = 'ok'
                    except Exception as e:
                        errors.append('Could not complete transaction')
                            
                else:
                    error_message = dom.getElementsByTagName('Verbiage')
                    errors.append('Transaction declined: %s' % error_message[0].firstChild.data)
            else:
                new_transactions = []
                for p in purchase_packages:
                    try:
                        package = Package.objects.get(pk=int(p[1]))
                        if package in new_packages:
                            new_transaction = Transaction(user=user)
                            new_transaction.package = package
                            if int(p[3]) == 1:
                                new_transaction.expires = date.today() + timedelta(days=365)
                                new_transaction.price = package.price
                            if int(p[3]) == 2:
                                new_transaction.expires = date.today() + timedelta(days=91)
                                new_transaction.price = package.per_file_price
                            if int(p[3]) == 3:
                                new_transaction.expires = date.today() + timedelta(days=30)
                                new_transaction.price = package.per_file_price
                            
                            new_transaction.type =  Transaction.CHEQUE
                            new_transaction.valid = False
                            new_transaction.save()
                            new_transactions.append(new_transaction)
                            
                        for t in update_transactions:
                            if t.package == package:
                                if int(p[3]) == 1:
                                    t.expires = t.expires + timedelta(days=365)
                                    t.price = package.price
                                if int(p[3]) == 2:
                                    t.expires = t.expires + timedelta(days=91)
                                    t.price = package.per_file_price
                                if int(p[3]) == 3:
                                    t.expires = t.expires + timedelta(days=30)
                                    t.price = package.per_file_price
                                
                                t.valid = False
                                t.save()
                                
                        
                        email_data = { }
                        email_data['update_transactions'] = update_transactions
                        email_data['new_transactions'] = new_transactions
                        email_data['user'] = user
                        email_data['profile'] = profile
                        email_data['payment_type'] = 'Cheque'
                        email_data['address'] =  template_data['address']
                        email_data['city'] = template_data['city'] 
                        email_data['country'] = template_data['country'] 
                        email_data['state'] = template_data['state']
                        email_data['zip'] = template_data['zip']
                        email_data['timestamp'] =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        request.session['update_transactions'] = update_transactions
                        request.session['new_transactions'] = new_transactions

                        send_email(['statistics@ific.ca', user.email], 'noreply@ific.ca', email_data, 'cheque_email.html', 'IFIC Package Purchase')
                        response['status'] = 'ok'
                        response['redirect'] = '/admin/purchase/summary'
                    except Package.DoesNotExist:
                        errors.append('Package does not exist')
                    except Exception as e:
                        errors.append('Could not complete transaction at this time')

    if len(errors) > 0:
        response['status'] = 'error'
        response['errors'] = errors
        
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')   
        
@login_required
def ajax_validate_transaction(request):
    response = { }
    errors = []
    user = request.user
    
    try:
        allowed = check_user_permissions(user, ['admin'])
    except Exception as e:
        allowed = False
    
    if allowed:
        if 'transaction' in request.GET:
            try:
                transaction = Transaction.objects.get(pk=int(request.GET['transaction']))
                if 'validate' in request.GET:
                    if int(request.GET['validate']) == 1:
                        transaction.valid = True
                        delta_time = date.today() - transaction.date
                        transaction.expires = transaction.expires + delta_time
                    else:
                        transaction.valid = False
                        
                    transaction.save()
                    response['status'] = 'ok'
            except Transaction.DoesNotExist:
                errors.append('Transaction ID does not exist')
            except Exception as e:
                errors.append('Could not validate transaction')
    else:
        errors.append('Invalid permissions')
        
    if len(errors) > 0:
        response['errors'] = errors
        response['status'] = 'error'
        
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')
   
@login_required    
def ajax_upload_next(request):
    response = { }
    errors = []
    if 'step' in request.session:
        step = int(request.session['step'])
    else:
        step = 0
    
    if 'contributer' in request.GET:
        try:
            contributer = Contributer.objects.get(pk=int(request.GET['contributer']))
            request.session['contributer'] = contributer
        except Contributer.DoesNotExist:
            errors.append('Group does not exist')

    if len(errors) == 0:
        if step < 2:
            step = step + 1
        else:
            step = 0
              
        request.session['step'] = step
        response['step'] = step
        response['status'] = 'ok' 
    else:
        response['status'] = 'error'
        response['errors'] = errors
    
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')       

@login_required
def ajax_upload_settings(request):
    user = request.user
    response = { }
    try:
        allowed = check_user_permissions(user, ['admin'])
    except Exception as e:
        allowed = False
    errors = []

    if allowed:
        upload_month = None
        cutoff_date = None
        if 'upload_month' in request.GET:
            upload_month = request.GET['upload_month']
        else:
            errors.append('No upload month provided')
            
        if 'cutoff_date' in request.GET:
            cutoff_date = request.GET['cutoff_date']
        else:
            errors.append('No cut off date provided')
        
        if 'report_view_date' in request.GET:
            report_view_date = request.GET['report_view_date']
        else:
            errors.append('No report view date provided')
            
        if len(errors) == 0:
            try:
                upload_setting = UploadSetting.objects.get(pk=1)
                upload_setting.upload_date = upload_month
                upload_setting.stop_upload_date = cutoff_date
                upload_setting.report_view_date = report_view_date
                
                upload_setting.save()
                response['status'] = 'ok'
            except UploadSetting.DoesNotExist:
                try:
                    upload_setting = UploadSetting(upload_date = upload_month, stop_upload_date=cutoff_date)
                    upload_setting.save()
                    response['status'] = 'ok'
                except Exception:
                    errors.append('Could not save settings')
        else:
            response['status'] = 'error'
    else:
        errors.append('Invalid permissions')
    
    if len(errors) != 0:
        response['status'] = 'error'
        response['errors'] = errors
        
        
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')      
        
@login_required
def ajax_validate(request):
    user = request.user
    response = { }
    
    try:
        allowed = check_user_permissions(user, ['admin', 'contributer'])
    except Exception as e:
        allowed = False
    
    if allowed:
        if 'contributer' in request.session:
            if 'template' in request.GET:
                contributer = request.session['contributer']
                response = validate_data(contributer, int(request.GET['template']), user)
    
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')      
 
# Generate 3 Industry Views    



def add_ific_header(list_data):
    
    try:
        upload_setting = UploadSetting.objects.get(pk=1)
        current_date = upload_setting.upload_date.strftime('%m/%d/%Y')
    except UploadSetting.DoesNotExist:
        current_date = datetime.now().strftime('%m/%d/%Y')
    
    
    list_data.append(['THE INVESTMENT FUND INSTITUTE OF CANADA'])
    list_data.append(['L\'INSTITU DES FOND D\'INVESTISSEMENT DU CANADA'])
    list_data.append(['Details by Member AS AT %s' % current_date])
    # Blank space
    list_data.append([])
    # Generate Headers
    #report_data.append(['Stand Alone View'])
    list_data.append(['IFIC ID Code', 'Group Code', 'Fund Code', 'Asset Class Type', 'CIFSC Asset Class Type', 'Investment Product Type', 'RRSP Eligible','Sales Fee',\
                        'Group Type', 'Group Name', 'Fund Name', 'Net Assets',\
                        'Cash & Short-term', 'Gross Sales', 'Reinvested Distribution', 'Gross Redemptions', 'Transfers In', 'Transfers Out',\
                        'Net Sales Inc. Reinv. Distr ', 'Net New Money', 'Net Sales Exc. Reinv. Distr', 'Unitholder', 'Capital Gain', 'Other Income', 'Index', 'Structure'])
        
    return list_data

def validate_data(contributer, template, user):
    
    errors = []
    warnings = []
    response = { }
    summary = { }

    try:
        setting = UploadSetting.objects.get(pk=1)
        current_date = setting.upload_date.strftime('%Y-%m')
    except UploadSetting.DoesNotExist:
        current_date = datetime.now().strftime('%Y-%m')
    
    file_name = '%s_template%d' % (current_date, template)
    file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, contributer.id, file_name)
    
    if not os.path.isfile(file_path):
        error = { }
        error['message'] = 'Template %d file not uploaded' % (template)
        error['row'] = 0
        error['column'] = 0
        errors.append(error)
    else:

        with open(file_path, 'U') as csv_file:   
            template_data = list(csv.reader(csv_file, dialect='excel-tab',  quoting=csv.QUOTE_NONE))

        if template == 1:
            fund_count = 0
            fund_columns = []
            total_column = 3
            line = 1
            for row in template_data:
                # Find the company code
                if line == 1:
                    column_count = 0
                    for column in row:
                        column = column.decode('utf-8')
                        column_count = column_count + 1
                        # Found company code
                        if len(column) == 3:
                            if contributer.code.lower() != column.lower():
                                error = { }
                                error['message'] = 'Invalid company code %s in column %d line %d' % (column, column_count, line)
                                error['column'] = column_count
                                error['row'] = line
                                errors.append(error)
                            
                # Check the fund codes
                if line == 2:
                    column_count = 0
                    for column in row:
                        # Found fund code
                        column = column.decode('utf-8')
                        column_count = column_count + 1
                        if column == 'TOTAL':
                            total_column = column_count

                        if len(column) <= 3 and len(column) > 0:
                            try:
                                # This makes sure that fund exists
                                fund = Fund.objects.get(code=column, contributer=contributer)
                                if fund.contributer != contributer and fund not in fund.funds.all():
                                    error = { }
                                    error['message'] = 'Company %s (%s) does not hold the fund or is not part of its FoF' % (contributer.name, contributer.code)
                                    error['column'] = column_count - 1
                                    error['row'] = line
                                    errors.append(error)
                                
                                
                                fund_count = fund_count + 1
                                fund_columns.append(column_count - 1)
                
                                            
                            except Fund.DoesNotExist:
                                error = { }
                                error['message'] = 'Fund not found %s in column %d line %d' % (column, column_count, line)
                                error['column'] = column_count - 1
                                error['row'] = line
                                errors.append(error)
                
                line = line + 1
                # End For Loop
                
            
            system_fund_count = Fund.objects.filter(contributer=contributer, active=True).count()
            
            # Make sure they are reporting on all their active funds
            if system_fund_count != fund_count:
                error = { }
                error['message'] = 'Invalid number of funds reported expecting %d fund(s) got %d fund(s)' % (system_fund_count, fund_count)
                error['column'] = 0
                error['row'] = 0
                errors.append(error)
            
            totals = []
            try:
                totals = get_column_data(template_data, total_column)
            except IndexError:
                error = { }
                error['message'] = 'Invalid template file'
                error['column'] = 0
                error['row'] = 0
                errors.append(error)
                
            if len(totals) == 13:            
                net_sales = round(float(totals[9].replace(',', '').replace('"', '').replace('$', '')), 2)
                gross_sales = round(float(totals[4].replace(',', '').replace('"', '').replace('$', '')), 2)
                reinvested_distribution = round(float(totals[5].replace(',', '').replace('"', '').replace('$', '')), 2)
                redemptions = round(float(totals[6].replace(',', '').replace('"', '').replace('$', '')), 2)
                transfers_in =  round(float(totals[7].replace(',', '').replace('"', '').replace('$', '')), 2)
                transfers_out =  round(float(totals[8].replace(',', '').replace('"', '').replace('$', '')), 2)
            
                calculated_net_sales = gross_sales + reinvested_distribution - redemptions + transfers_in - transfers_out
                
                if net_sales != calculated_net_sales:
                    error = { }
                    error['message'] = 'Invalid net sales calculations'
                    error['column'] = total_column
                    error['row'] =  9
                    errors.append(error)
                    response['net_sales'] = net_sales
                    response['calc_net_sales'] = calculated_net_sales
            

                summary = { }
                
                summary['net_total_assets'] = 0
                summary['cash_short_term'] = 0
                summary['gross_sales'] = 0
                summary['reinvested'] = 0
                summary['redemptions'] = 0
                summary['transfers_in'] = 0
                summary['transfers_out'] = 0
                summary['net_sales'] = 0
                summary['unit_holders'] = 0
                summary['capital_gains'] = 0
                summary['income_actual'] = 0
                
                current_month = int(setting.upload_date.strftime('%m'))
                current_year = int(setting.upload_date.strftime('%Y'))
                last_month = 0
                year = 0
                
                if current_month == 1:
                    last_month = 12 
                    year = current_year - 1
                else:
                    last_month = current_month - 1
                    year = current_year
                
                last_month_date = "%s-%s" % (year, last_month)
                file_name = '%s_template1' % last_month_date
                file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, contributer.id, file_name)
                
                last_month_data = list()
                if os.path.isfile(file_path):
                     with open(file_path, 'U') as csv_file:   
                         last_month_data = list(csv.reader(csv_file, dialect='excel-tab'))
                else:
                    pass
                    #warning = { }
                    #warning['message'] = 'Could not run co anal check, do not have last month\'s data'
                    #warning['row'] = 0
                    #warning['column'] = 0
                    #warnings.append(warning)
                
                
                template_two_data = list()
                file_name_template2 = '%s_template2' % current_date
                file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, contributer.id, file_name_template2)
                if os.path.isfile(file_path):
                     with open(file_path, 'U') as csv_file:   
                         template_two_data = list(csv.reader(csv_file, dialect='excel-tab'))
                else:
                    if Fund.objects.filter(contributer=contributer, investment_type=InvestmentType(pk=2)).count() > 0:
                        warning = { }
                        warning['message'] = 'Could not run FoF report check, do not have template 2 data'
                        warning['row'] = 0
                        warning['column'] = 0
                        warnings.append(warning)
                
                
                template_three_data = list()
                file_name_template3 = '%s_template3' % current_date
                file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, contributer.id, file_name_template3)
                if os.path.isfile(file_path):
                     with open(file_path, 'U') as csv_file:   
                         template_three_data = list(csv.reader(csv_file, dialect='excel-tab'))
                else:
                    if Fund.objects.filter(contributer=contributer, investment_type=InvestmentType(pk=3)).count() > 0 or Fund.objects.filter(contributer=contributer, investment_type=InvestmentType(pk=4)).count() > 0:
                        warning = { }
                        warning['message'] = 'Could not run Proprietary Fof report check, do not have template 3 data'
                        warning['row'] = 0
                        warning['column'] = 0
                        warnings.append(warning)
                
                
                last_month_fund_columns = []
                if len(last_month_data) > 0:
                    line = 0
                    for row in last_month_data:
                        if line == 1:
                            last_column_count = 0
                            for column in row:
                                # Found fund
                                if len(column) <= 3:
                                    last_month_fund_columns.append(last_column_count)
                                
                                last_column_count = last_column_count + 1
                                # End For Loop
                        # End For Loop
                        line = line + 1
                
                for column in fund_columns:
                    fund_data = get_column_data(template_data, column)    

                    # Last month data
                    if len(last_month_fund_columns) > 0:
                        for last_month_fund_column in last_month_fund_columns:
                            last_month_fund_data = get_column_data(last_month_data, last_month_fund_column)
                            
                            
                            if last_month_fund_data[1] == fund_data[1]:
                                row_check = 0
                                
                                for data in fund_data[2:]:
                                    row_check += 1
                                    if float(data.replace(',', '').replace('"', '').replace('$', '')) > 0.00 and data in last_month_fund_data:
                                        warning = { }
                                        warning['message'] = 'Duplicate data $%.2f found in historical data in column %d for fund %s' % (float(data), column_count, fund_data[1])
                                        warning['column'] = column
                                        warning['row'] = row_check 
                                        warnings.append(warning)

                    
                                # Anal fund check
                                current_net_assets = float(fund_data[2].replace(',', '').replace('"', '').replace('$', ''))
                                last_month_net_assets = float(last_month_fund_data[2].replace(',', '').replace('"', '').replace('$', ''))
                                gross_sales = float(fund_data[4].replace(',', '').replace('"', '').replace('$', ''))
                                gross_redemptions = float(fund_data[6].replace(',', '').replace('"', '').replace('$', ''))
                                transfers_in = float(fund_data[7].replace(',', '').replace('"', '').replace('$', ''))
                                transfers_out = float(fund_data[8].replace(',', '').replace('"', '').replace('$', ''))
                                market_effect = 0
                                merger_effect = 0
                                
                                current_month_net_sales_exec = gross_sales - gross_redemptions + transfers_in - transfers_out
                                divisor = last_month_net_assets + current_month_net_sales_exec
                                
                                if divisor > 0:
                                    market_effect = (current_net_assets / (last_month_net_assets + current_month_net_sales_exec)) - 1
                                else:
                                    warning = { }
                                    warning['message'] = 'Net Sales Exc. Dist. is Zero'
                                    warning['row'] = 0 
                                    warning['column'] = 0
                                    warnings.append(warning)
                                    
                                
                                if market_effect >= 0.15:
                                    warning = { }
                                    warning['message'] = 'Market effect %.2f %% is greater than 15%% on fund %s' % (float(market_effect * 100), fund_data[1])
                                    warning['row'] = 0 
                                    warning['column'] = 0
                                    warnings.append(warning)
                                
                                if last_month_net_assets > 0:
                                    merger_effect = abs(current_month_net_sales_exec / last_month_net_assets) - 1
                                else:
                                    warning = { }
                                    warning['message'] = 'Last month net assets is Zero'
                                    warning['row'] = 0 
                                    warning['column'] = 0
                                    warnings.append(warning)
                                    
                                    
                                if merger_effect > 0.15:
                                    warning = { }
                                    warning['message'] = 'Merger effect %.2f %% is greater than 15%% on fund %s' % (float(merger_effect * 100), fund_data[1])
                                    warning['row'] = 0 
                                    warning['column'] = 0
                                    warnings.append(warning)
                           
                        template_2_row_count = 0   
                        for two_data in template_two_data:                            
                            if len(two_data) > 0:
                                if len(two_data[0]) <= 7:
                                    if two_data[0].strip().find('*'):
                                        ific_code = two_data[0].split('*')
                                        
                                        if len(ific_code) > 1:
                                            if ific_code[1].lower() == fund_data[1].lower():
                                                
                                                if float(two_data[2].replace(',', '').replace('"', '').replace('$', '')) > float(fund_data[2].replace(',', '').replace('"', '').replace('$', '')):
                                                    warning = { }
                                                    warning['message'] = 'Net assets greater in template 2 greater than template 1 for fund %s' % ific_code[1]
                                                    warning['column'] = column
                                                    warning['row'] = 2
                                                    warnings.append(warning)
                                                
                                                if float(two_data[3].replace(',', '').replace('"', '').replace('$', '')) > float(fund_data[4].replace(',', '').replace('"', '').replace('$', '')):
                                                    warning = { }
                                                    warning['message'] = 'Gross purchases greater in template 2 than template 1 for fund %s' % ific_code[1]
                                                    warning['column'] = column
                                                    warning['row'] = 4
                                                    warnings.append(warning)
                                               
                                                if float(two_data[4].replace(',', '').replace('"', '').replace('$', '')) > float(fund_data[6].replace(',', '').replace('"', '').replace('$', '')):
                                                    warning = { }
                                                    warning['message'] = 'Gross Redemptions greater in template 2 than template 1 for fund %s' % ific_code[1]
                                                    warning['column'] = column
                                                    warning['row'] = 6
                                                    warnings.append(warning)
                        
                        
                        for three_data in template_three_data:
                            if len(three_data) > 0:
                                if len(three_data[0]) <= 7:
                                    if three_data[0].strip().find('*'):
                                        ific_code = three_data[0].split('*')
                                        if len(ific_code) > 1:
                                            if ific_code[1].lower() == fund_data[1].lower():
                                                if float(three_data[2].replace(',', '').replace('"', '').replace('$', '')) > float(fund_data[2].replace(',', '').replace('"', '').replace('$', '')):
                                                    warning = { }
                                                    warning['message'] = 'Net assets greater in template 3 greater than template 1'
                                                    warning['row'] = 2
                                                    warning['column'] = column
                                                    warnings.append(warning)
                                            
                                                if float(three_data[3].replace(',', '').replace('"', '').replace('$', '')) > float(fund_data[4].replace(',', '').replace('"', '').replace('$', '')):
                                                    warning = { }
                                                    warning['message'] = 'Gross purchases greater in template 3 than template 1'
                                                    warning['row'] = 4
                                                    warning['column'] = column
                                                    warnings.append(warning)
                                           
                                                if float(three_data[4].replace(',', '').replace('"', '').replace('$', '')) > float(fund_data[6].replace(',', '').replace('"', '').replace('$', '')):
                                                    warning = { }
                                                    warning['message'] = 'Gross Redemptions greater in template 2 than template 1'
                                                    warning['row'] = 6
                                                    warning['column'] = column
                                                    warnings.append(warning)
                
                    # Summary values
                    summary['net_total_assets'] = summary['net_total_assets'] + float(fund_data[2].replace(',', '').replace('"', '').replace('$', ''))
                    summary['cash_short_term'] = summary['cash_short_term'] + float(fund_data[3].replace(',', '').replace('"', '').replace('$', ''))
                    summary['gross_sales'] = summary['gross_sales'] + float(fund_data[4].replace(',', '').replace('"', '').replace('$', ''))
                    summary['reinvested'] = summary['reinvested'] + float(fund_data[5].replace(',', '').replace('"', '').replace('$', ''))
                    summary['redemptions'] = summary['redemptions'] + float(fund_data[6].replace(',', '').replace('"', '').replace('$', ''))
                    summary['transfers_in'] = summary['transfers_in'] + float(fund_data[7].replace(',', '').replace('"', '').replace('$', ''))
                    summary['transfers_out'] = summary['transfers_out'] + float(fund_data[8].replace(',', '').replace('"', '').replace('$', ''))
                    summary['net_sales'] = summary['net_sales'] + float(fund_data[9].replace(',', '').replace('"', '').replace('$', ''))
                    summary['unit_holders'] = summary['unit_holders'] + float(fund_data[10].replace(',', '').replace('"', '').replace('$', ''))
                    summary['capital_gains'] = summary['capital_gains'] + float(fund_data[11].replace(',', '').replace('"', '').replace('$', ''))
                    summary['income_actual'] = summary['income_actual'] + float(fund_data[12].replace(',', '').replace('"', '').replace('$', ''))
                    
                    if (float(fund_data[11].replace(',', '').replace('"', '').replace('$', '')) + float(fund_data[12].replace(',', '').replace('"', '').replace('$', ''))) < float(fund_data[5].replace(',', '').replace('"', '').replace('$', '')):
                        warning = { }
                        warning['message'] = 'Capital gains and income less than reinvested distribution for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 5
                        warnings.append(warning)
                    
                    if float(fund_data[3].replace(',', '').replace('"', '').replace('$', '')) > float(fund_data[2].replace(',', '').replace('"', '').replace('$', '')):
                        warning = { }
                        warning['message'] = 'Cash & Short-term is greater than assets for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 2
                        warnings.append(warning)
                    
                    if float(fund_data[10].replace(',', '').replace('"', '').replace('$', '')) == 0:
                        warning = { }
                        warning['message'] = 'Unit holders equals 0 for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 10
                        warnings.append(warning)
                        
                    if float(fund_data[10].replace(',', '').replace('"', '').replace('$', '')) < 10:
                        warning = { }
                        warning['message'] = 'Unit holders less than 10 for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 10                        
                        warnings.append(warning)
                    
                    #if float(fund_data[12].replace(',', '').replace('"', '').replace('$', '')) < 10:
                    #    warning = { }
                    #    warning['message'] = 'Income less than 10 for fund %s' % fund_data[1]
                    #    warning['column'] = column
                    #    warning['row'] = 12  
                    #    warnings.append(warning)
                    
                        
                    if float(fund_data[2].replace(',', '').replace('"', '').replace('$', '')) < 0:
                        warning = { }
                        warning['message'] = 'Net Total Assets unexpected negative for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 2                         
                        warnings.append(warning)
                        
                    if float(fund_data[3].replace(',', '').replace('"', '').replace('$', '')) < 0:
                        warning = { }
                        warning['message'] = 'Cash & Short-term unexpected negative for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 3                            
                        warnings.append(warning)
                        
                    if float(fund_data[4].replace(',', '').replace('"', '').replace('$', '')) < 0:
                        warning = { }
                        warning['message'] = 'Gross sales unexpected negative for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 4                         
                        warnings.append(warning)
                        
                    if float(fund_data[5].replace(',', '').replace('"', '').replace('$', '')) < 0:
                        warning = { }
                        warning['message'] = 'Reinvested distribution unexpected negative for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 5                             
                        warnings.append(warning)
                        
                    if float(fund_data[6].replace(',', '').replace('"', '').replace('$', '')) < 0:
                        warning = { }
                        warning['message'] = 'Redemptions distribution unexpected negative for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 6                           
                        warnings.append(warning)
                
                    if float(fund_data[7].replace(',', '').replace('"', '').replace('$', '')) < 0:
                        warning = { }
                        warning['message'] = 'Transfers-IN unexpected negative for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 7 
                        warnings.append(warning)
                        
                    if float(fund_data[8].replace(',', '').replace('"', '').replace('$', '')) < 0:
                        warning = { }
                        warning['message'] = 'Transfers-OUT unexpected negative for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 8 
                        warnings.append(warning)
                        
                    if float(fund_data[10].replace(',', '').replace('"', '').replace('$', '')) < 0:
                        warning = { }
                        warning['message'] = 'Unitholders unexpected negative for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 10 
                        warnings.append(warning)
                        
                    if float(fund_data[11].replace(',', '').replace('"', '').replace('$', '')) < 0:
                        warning = { }
                        warning['message'] = 'Capital Gains unexpected negative for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 11 
                        warnings.append(warning)
                        
                    if float(fund_data[12].replace(',', '').replace('"', '').replace('$', '')) < 0:
                        warning['message'] = 'Income - Actual unexpected negative for fund %s' % fund_data[1]
                        warning['column'] = column
                        warning['row'] = 12 
                        warnings.append(warning)

                    if len(warnings) > 0:
                        response['warnings'] = warnings
            else:
                error = { }
                error['message'] = 'Not enough data provided in file'
                error['column'] = total_column
                error['row'] = 0
                errors.append(error)
            

         
        # Validate template 2
        if template == 2 or template == 3:

            summary = { }
            # Template 1 also needs to be opened
            file_name = '%s_template1' % (current_date)
            file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, contributer.id, file_name)
            
            if not os.path.isfile(file_path):
                error = { }
                error['message'] = 'Template 1 file not uploaded'
                error['column'] = 0
                error['row'] = 0
                errors.append(error)
            else:

                with open(file_path, 'U') as csv_file:   
                    template_one_data = list(csv.reader(csv_file, dialect='excel-tab'))
                
                if template == 2:
                    template_three_data = list()
                    file_name_template3 = '%s_template3' % current_date
                    file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, contributer.id, file_name_template3)
                    if os.path.isfile(file_path):
                         with open(file_path, 'U') as csv_file:   
                             template_three_data = list(csv.reader(csv_file, dialect='excel-tab'))
                    else:
                        warning = { }
                        warning['message'] = 'Could not run Proprietary Fof report check, do not have template 3 data'
                        warning['row'] = 0
                        warning['column'] = 0
                        warnings.append(warning)
                
                
                current_month = int(setting.upload_date.strftime('%m'))
                current_year = int(setting.upload_date.strftime('%Y'))
                last_month = 0
                year = 0
            
                if current_month == 1:
                    last_month = 12 
                    year = current_year - 1
                else:
                    last_month = current_month - 1
                    year = current_year
                
                last_month_date = "%s-%s" % (year, last_month)
                file_name = '%s_template%d' % (last_month_date, template)
                file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, contributer.id, file_name)
            
                last_month_data = list()
                if os.path.isfile(file_path):
                    with open(file_path, 'U') as csv_file:   
                        last_month_data = list(csv.reader(csv_file, dialect='excel-tab'))
                else:
                    warning = { }
                    warning['message'] = 'Could not run co anal check, do not have last month\'s data'
                    warning['row'] = 0
                    warning['column'] = 0
                    warnings.append(warning)
                    

                line = 1
                allowed_funds = []
                #template_one_fund_codes = template_one_data[1][4:]                
                allowed_underlying_funds = []
                reported_ific_fund_codes = []
                fund_rows = []

                summary['asset_total'] = 0
                summary['purchase_total'] = 0
                summary['redemption_total'] = 0
                summary['transfers_in_total'] = 0
                summary['transfers_out_total'] = 0
                
                allowed_funds = AllowedTemplate.objects.filter(contributer=contributer, template_type = template)
                
                fund_code_column_count = 4
                for allowed in allowed_funds:
                    allowed_underlying_funds.append(allowed.fund.code.upper())
                    
                
                for fund_data in template_data:
                    if len(fund_data) <= 7:
                        if line == 1:
                            if len(fund_data) > 0:
                                if len(fund_data[0]) > 0:
                                    if fund_data[0].strip() != 'IFIC ID Code':
                                        error = { }
                                        error['message'] = 'IFIC ID Code Label is missing at row 1 column 1'
                                        error['row'] = 1
                                        error['column'] = 1
                                        errors.append(error) 
                                
                                if len(fund_data[1]) > 0:                                
                                    if fund_data[1].strip() != 'Description':
                                        error = { }
                                        error['message'] = 'Description Header is missing at row 1 column 2'
                                        error['row'] = 1
                                        error['column'] = 2                                    
                                        errors.append(error)
                                        
                                if len(fund_data[2]) > 0:
                                    if fund_data[2].strip() != 'Net Assets':
                                        error = { }
                                        error['message'] = 'Net Assets Header is missing at row 1 column 3'
                                        error['row'] = 1
                                        error['column'] = 3                                           
                                        errors.append(error)
                                        
                                if len(fund_data[3]) > 0:
                                    if fund_data[3].strip() != 'Gross Purchases':
                                        error = { }
                                        error['message'] = 'Gross Purchases Header is missing at row 1 column 4'
                                        error['row'] = 1
                                        error['column'] = 4                                               
                                        errors.append(error)
                                
                                if len(fund_data[4]) > 0:
                                    if fund_data[4].strip() != 'Gross Redemptions':
                                        error = { }
                                        error['message'] = 'Gross Redemptions Header is missing at row 1 column 5'
                                        error['row'] = 1
                                        error['column'] = 5                                       
                                        errors.append(error)
                                
                                if len(fund_data[5]) > 0:  
                                    if fund_data[5].strip() != 'Transfers In':
                                        error = { }
                                        error['message'] = 'Transfers In Header is missing at row 1 column 6'
                                        error['row'] = 1
                                        error['column'] = 6                                    
                                        errors.append(error)
                                        
                                if len(fund_data[6]) > 0:
                                    if fund_data[6].strip() != 'Transfers Out':
                                        error = { }
                                        error['message'] = 'Transfers Out Header is missing at row 1 column 7'
                                        error['row'] = 1
                                        error['column'] = 7                                       
                                        errors.append(error)
                            
                        if line == 2:
                            if len(fund_data) > 0:
                                if len(fund_data[0]) > 0:
                                    if fund_data[0].strip() != 'CASH':
                                        error = { }
                                        error['message'] = 'CASH Label is missing at row 2 column 1'
                                        error['row'] = 2
                                        error['column'] = 1                                      
                                        errors.append(error)                         
                        
                        if line == 3:
                            if len(fund_data) > 0:
                                if len(fund_data[0]) > 0:
                                    if fund_data[0].strip() != 'OTHER':
                                        error = { }
                                        error['message'] = 'OTHER Label is missing at row 3 column 1'
                                        error['row'] = 3
                                        error['column'] = 1                                           
                                        errors.append(error)
                                        
                        if line > 3:
                             if len(fund_data) > 0:
                                 ific_code = fund_data[0].strip()
                                 if ific_code.find('*'):
                                     split_code = ific_code.split('*')
                                     
                                     if len(split_code) > 1:
                
                                         if len(split_code[0]) > 3:
                                             error = { }
                                             error['message'] = 'Invalid group code found in IFIC code line %d column 1 (Incorrect length)' % line
                                             error['row'] = line
                                             error['column'] = 1                                         
                                             errors.append(error)
                                            
                                        
                                         if len(split_code[1]) > 3:
                                             error = { }
                                             error['message'] = 'Invalid fund code found in IFIC code line %d column 1 (Incorrect length)' % line
                                             error['row'] = line
                                             error['column'] = 1                                           
                                             errors.append(error)
                    
                                         try:
            
                                             
                                             try:
                                                 current_contributer = Contributer.objects.get(code__iexact=split_code[0])
                                             except Contributer.DoesNotExist:
                                                 error = { }
                                                 error['message'] = 'Fund contributer does not exist'
                                                 error['row'] = line
                                                 error['column'] = 1
                                                 errors.append(error)
                                             
                                             sa_fund = Fund.objects.get(code__iexact=split_code[1], contributer=current_contributer)
                                             
                                             if sa_fund.investment_type.fund_of_fund != 0:
                                                 error = { }
                                                 error['message'] = 'Fund %s in IFIC code % is not a Stand-alone mutual fund' % (split_code[1], ific_code)
                                                 error['row'] = line
                                                 error['column'] = 1
                                                 errors.append(error)
                                             else:
                                                 reported_ific_fund_codes.append(sa_fund.code.upper())
                                     
                                                
                                                 current_net_assets = float(fund_data[2].replace(',', '').replace('"', '').replace('$', ''))
                                                 gross_purchases = float(fund_data[3].replace(',', '').replace('"', '').replace('$', ''))
                                                 gross_redemptions = float(fund_data[4].replace(',', '').replace('"', '').replace('$', ''))
                                                 transfers_in = float(fund_data[5].replace(',', '').replace('"', '').replace('$', ''))
                                                 transfers_out = float(fund_data[6].replace(',', '').replace('"', '').replace('$', ''))
                                            
                                                 if current_net_assets == 0.00:
                                                     warning = { }
                                                     warning['message'] = 'Current month net assets for %s is 0' % split_code[1]
                                                     warning['row'] = line
                                                     warning['column'] = 2
                                                     warnings.append(warning)
                                                 
                                                 if template == 2:
                                                     for three_data in template_three_data:
                                                         if len(three_data) > 0:
                                                             if three_data[0].find('*'):
                                                                 fof_ific_code = three_data[0].strip().split('*')
                                                                 if len(split_code) > 1 and len(fof_ific_code) > 1:
                                                                     if fof_ific_code[1].upper() == split_code[1].upper() and fof_ific_code[0].upper() == split_code[0].upper():
                                                                         if float(three_data[2].replace(',', '').replace('"', '').replace('$', '')) > current_net_assets:                                        
                                                                             warning = { }
                                                                             warning['message'] = 'Template 3 net assets greater than template 2 for %s' % three_data[0].strip()
                                                                             warning['row'] = line
                                                                             warning['column'] = 2
                                                                             warnings.append(warning)
                                                                         if float(three_data[3]) > gross_purchases:
                                                                             warning = { }
                                                                             warning['message'] = 'Template 3 gross purchases greater than template 2 for %s' % three_data[0].strip()
                                                                             warning['row'] = line
                                                                             warning['column'] = 3
                                                                             warnings.append(warning)
                                                                         if float(three_data[4]) > gross_redemptions:
                                                                             warning = { }
                                                                             warning['message'] = 'Template 3 gross redemptions greather than template 2 for %s' % three_data[0].strip()
                                                                             warning['row'] = line
                                                                             warning['column'] = 4
                                                                             warnings.append(warning)
    
                                                 last_month_net_assets = 0.00
                                                 for last_data in last_month_data:
                                                     if len(last_data) > 0:
                                                          if last_data[0].find('*'):
                                                             fof_ific_code = last_data[0].strip().split('*') 
                                                             if len(split_code) > 1 and len(fof_ific_code) > 1:
                                                                 if fof_ific_code[1].upper() == split_code[1].upper() and fof_ific_code[0].upper() == split_code[0].upper():
                                                                     last_month_net_assets = float(last_data[2].replace(',', '').replace('"', '').replace('$', ''))
        
                                                                     if last_month_net_assets == float(fund_data[2].replace(',', '').replace('"', '').replace('$', '')):
                                                                         warning = { }
                                                                         warning['message'] = 'Duplicate data found for net assets from last month data %.2f' % float(last_data[2])
                                                                         warning['row'] = line
                                                                         warning['column'] = 2
                                                                         warnings.append(warning)
                                                                     if float(last_data[3]) == gross_purchases:
                                                                         warning = { }
                                                                         warning['message'] = 'Duplicate data found for gross purchases from last month data %.2f' % float(last_data[3])
                                                                         warning['row'] = line
                                                                         warning['column'] = 3
                                                                         warnings.append(warning)
                                                                     if float(last_data[4]) == gross_redemptions:
                                                                         warning = { }
                                                                         warning['message'] = 'Duplicate data found for gross redemptions from last month data %.2f' % float(last_data[4])
                                                                         warning['row'] = line
                                                                         warning['column'] = 4
                                                                         warnings.append(warning)
                                                                     if float(last_data[5]) == transfers_in:
                                                                         warning = { }
                                                                         warning['message'] = 'Duplicate data found for transfers in from last month data %.2f' % float(last_data[3])
                                                                         warning['row'] = line
                                                                         warning['column'] = 5
                                                                         warnings.append(warning)
                                                                     if float(last_data[6]) == transfers_out:
                                                                         warning = { }
                                                                         warning['message'] = 'Duplicate data found for transfers out from last month data %.2f' % float(last_data[4])
                                                                         warning['row'] = line
                                                                         warning['column'] = 6
                                                                         warnings.append(warning)
                                                                 
                                                                     break
                      
                                                 if len(last_month_data) > 0:
                                                     current_month_net_sales_exec = gross_purchases - gross_redemptions + transfers_in - transfers_out
                                                     
                                                     divisor = float(last_month_net_assets + current_month_net_sales_exec)
                                                     market_effect = 0
                                                     merger_effect = 0
    
                                                     if divisor != 0:
                                                         market_effect = (current_net_assets / divisor) - 1
                                                     else:
                                                         warning = { }
                                                         warning['message'] = 'Net Sales Exc. Dist is 0 for fund %s' % split_code[1]
                                                         warning['row'] = line
                                                         warning['column'] = 0
                                                         warnings.append(warning)
                                                     
                                                     if market_effect > 0.15:
                                                         warning = { }
                                                         warning['message'] = 'Market effect greater than 15%% for fund %s' % split_code[1]
                                                         warning['row'] = line
                                                         warning['column'] = 0                                                     
                                                         warnings.append(warning)
                                                     
                                                     if last_month_net_assets > 0:
                                                         merger_effect = abs(current_month_net_sales_exec / last_month_net_assets) - 1
                                                     else:
                                                         warning = { }
                                                         warning['message'] = 'Could not calculate merger effect last month net assets is 0'
                                                         warning['row'] = line
                                                         warning['column'] = 2     
                                                         warnings.append(warning)
                                                         
                                                     if merger_effect > 0.15:
                                                        warning = { }
                                                        warning['message'] = 'Merger effect greater than 15%% for fund %s' % split_code[1]
                                                        warning['row'] = line
                                                        warning['column'] = 0                                                     
                                                        warnings.append(warning)
                                                     
                                                 summary['asset_total'] = summary['asset_total'] + current_net_assets
                                                 summary['purchase_total'] = summary['purchase_total'] + gross_purchases
                                                 summary['redemption_total'] = summary['redemption_total'] + gross_redemptions
                                                 summary['transfers_in_total'] = summary['transfers_in_total'] + transfers_in
                                                 summary['transfers_out_total'] = summary['transfers_out_total'] + transfers_out
                                                 
                                         except Fund.DoesNotExist:
                                             pass
                                             #error = { }
                                             #error['message'] = 'Fund %s does not exist in system line %d column 1' % (split_code[1], line)
                                             #error['row'] = line
                                             #error['column'] = 1
                                             #errors.append(error)
                    else:
                        error = { }
                        error['message'] = 'Invalid template format'
                        error['row'] = 0
                        error['column'] = 0
                        errors.append(error)
                        break
                                 
                    line = line + 1
                    # End for loop

                
                if len(reported_ific_fund_codes) > 0:
                    for sa in allowed_underlying_funds:
                        if sa.upper() not in reported_ific_fund_codes:
                            error = { }
                            error['message'] = 'Missing stand alone fund %s' % sa.upper()
                            error['row'] = 0
                            error['column']= 0
                            errors.append(error)
                    
                    for reported in reported_ific_fund_codes:
                        if reported.upper() not in allowed_underlying_funds:
                            error = { }
                            error['message'] = 'Not allowed to report on this fund %s' % reported
                            error['row'] = 0
                            error['column']= 0
                            errors.append(error)
                else:
                    error = { }
                    error['message'] = 'No funds reported'
                    error['row'] = 0
                    error['column'] = 0
                    errors.append(error) 
                    
    try:
        
        validation = ValidTemplate.objects.get(contributer=contributer, date__year=setting.upload_date.strftime('%Y'), date__month=setting.upload_date.strftime('%m'))
    except ValidTemplate.DoesNotExist:
        try:
            validation = ValidTemplate(contributer=contributer, date=setting.upload_date.strftime('%Y-%m-%d'))
            validation.save()
        except Exception as e:
            errors.append('Could not complete validation process')
        
    # Delete current errors with template
    TemplateError.objects.filter(valid_template=validation, template=template).delete()
    
    if len(errors) == 0:
        response['status'] = 'ok'
        response['summary'] = summary
        
        if template == 1:
            validation.template_one = True
        if template == 2:
            validation.template_two = True
        if template == 3:
            validation.template_three = True
            
        validation.save()
    else:          
        response['status'] = 'error'
        response['errors'] = errors
        

        for error in errors:
            try:
                e = TemplateError.objects.create(valid_template=validation, template=template, error=error['message'], error_type=1, row=error['row'], column=error['column'])
                e.save()
            except Exception as e:
                response['status'] = 'error'
                response['errors'] = errors.append('Could not save errors')
    
    if len(summary) > 0:
        response['summary'] = summary
    
    if len(warnings) > 0:
        
        for warning in warnings:
            try:
                w = TemplateError.objects.create(valid_template=validation, template=template, error=warning['message'], error_type=0, row=warning['row'], column=warning['column'])
                w.save()
            except Exception as e:
                response['status'] = 'error'
                response['errors'] = errors.append('Could not sae warnings')
            
        response['warnings'] = warnings
    
    return response

def get_column_data(matrix, x):
    return [row[x] for row in matrix]

@csrf_exempt
def ajax_save_report(request, id = None, template = None):
    errors = []
    response = { }
    
    try:
        if id != None:
            contributer = Contributer.objects.get(pk=id)
        else:
            errors.append('No group sent')
        
        if template != None:
            if template < 0 and template > 2:
                errors.append('Invalid template')
        else:
            errors.append('No template sent')
        
        setting = UploadSetting.objects.get(pk=1)
        date = setting.upload_date.strftime('%Y-%m')
        
        if template:
            file_name = '%s_template%s' % (date, template)
            file_path = '%s/uploads/%d/%s.csv' % (settings.MEDIA_ROOT, contributer.id, file_name)
                    
            template_data = simplejson.loads(request.raw_post_data)
            
            if len(template_data) > 0:
                if os.path.isfile(file_path):            
                    try:
                        csv_writer = csv.writer(open(file_path, 'wb'), dialect=csv.excel_tab)
                        for data in template_data:
                            csv_writer.writerow(data)
                        response['status'] = 'ok'
                    except:
                        errors.append('Could not save file')
                else:
                    errors.append('Template does not exist')
            else:
                errors.append('Data not sent')
            
    except UploadSetting.DoesNotExist:
        errors.append('Upload date not defined') 
    except Contributer.DoesNotExist:
        errors.append('Group does not exist')
        
    if len(errors) > 0:
        response['status'] = 'error'
        
    response['errors'] = errors    
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response, mimetype='application/json')    

def send_view_completed_email(template_data):
    try:
        message = render_to_string('view_complete_email.html', template_data)
        send_mail('%s Completed' % (template_data['view']), message, 'admin@ific.com', ['statistics@ific.ca'], fail_silently=False)
    except Exception as e:
        print e
          
