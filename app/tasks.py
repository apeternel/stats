import os
import settings


# Models
from app.models import CompanyType,  FundCategory, UploadSetting, AllowedTemplate,\
Industry, InvestmentType, Contributer, Fund, FundType, TemplateError, UserLog, UserProfile, UserType, ValidTemplate, Transaction, Package, Reports

from app.views.ajax.views import add_ific_header

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
                                                fund.investment_type.name, 'Y' if fund.rrsp else 'N', sales_fee, fund.classification.name, '%s' % contributer.industry.name, \
                                                contributer.name, fund_name, fund_index, fund_structure,'%.2f' % net_assets, '%.2f' % cash, '%.2f' % gross_sales, '%.2f' % reinvested_distribution, \
                                                '%.2f' % gross_redemptions, '%.2f' % transfers_in, '%.2f' % transfers_out,\
                                                '%2f' % net_sales, '%.2f' % net_new_money, unitholder, '%.2f' % capital_gains, '%.2f' % other_income])
                    except Exception as e:
                        pass
                        # warnings.append('Could not find fund %s for group %s in system' % (fund_code, contributer.code))
            
                index = index + 1
            
            report_data.append(['', '%s Total' % contributer.code.upper(), '', '', '', '', '', '', '', '', '', '', '', '',\
                                '%.2f' % net_assets_total, '%.2f' % cash_total, '%.2f' % gross_sales_total, '%.2f' % reinvested_distribution_total,\
                                '%.2f' % gross_redemptions_total, '%.2f' % transfers_in_total, '%.2f' % transfers_out_total, '%.2f' % net_sales_total,\
                                '%.2f' % net_new_money_total, unitholder_total, '%.2f' % capital_gains_total, '%.2f' % other_income_total])
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
            csv_writer.writerow(data)
            
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
        
    return response



