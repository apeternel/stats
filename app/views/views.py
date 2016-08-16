# Includes

import csv
import datetime
import mimetypes
import os
import time
import settings
import math

from settings import STATES, MAILING_LIST_ID
import mailchimp

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.db import IntegrityError
from django.core.validators import email_re
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail

from app.models import Industry, CompanyType, Contributer, Fund, FundCategory, FundClassification, FundType, InvestmentType\
, Package, UserLog, UserProfile, UserType, TemplateError, Transaction, ValidTemplate, Reports, UploadSetting, AllowedTemplate



def check_user_permissions(user, user_type):
    try:
        user_profile = UserProfile.objects.get(user=user)
        
        type = user_profile.user_type.type
        return type in user_type
    except UserProfile.DoesNotExist:
        raise Exception('User profile does not exist')

# Public Views
def home(request):
    
    user = request.user
    template_data = { }
    
    template_data['user'] = user
    
    return render_to_response('home.html', template_data)

def home_info(request):
    
    user = request.user
    
    template_data = { }
    
    template_data['user'] = user
    
    return render_to_response('home_info.html', template_data)

def privacy(request):
    
    user = request.user
    
    template_data = { }
    
    template_data['user'] = user
    
    return render_to_response('privacy.html', template_data)

def terms(request):
    
    user = request.user
    
    template_data = { }
    
    template_data['user'] = user
    
    return render_to_response('terms.html', template_data)

# User Views
@login_required(login_url='/admin/login')
def utilities(request):
    
    template_data = { }
    user = request.user    

    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except Exception as e:
        template_data['allowed'] = False
    
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        pass
    
    template_data['url'] = 'utilities'
    template_data['profile'] = profile
    template_data['user'] = user
    
    return render_to_response('utilities.html', template_data)

@login_required(login_url='/admin/login')
def users(request):
    user = request.user
    
    template_data = { }
    
    template_data.update(csrf(request))
    
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except Exception as e:
        template_data['allowed'] = False
        
    
    users = User.objects.all()
    user_profiles = []
    
    for u in users:
        try:
            profile = UserProfile.objects.get(user=u)
            u.profile = profile
            user_profiles.append(u)
        except:
            pass

    if request.method == 'POST':
        users = []
        if 'search_user' in request.POST:
            template_data['search_user'] = request.POST['search_user']
            if 'user' in request.POST:
                if len(request.POST['user']) > 0:
                    try:
                        users = User.objects.filter(pk=int(request.POST['user']))
                    except User.DoesNotExist:
                        pass
        else:
            users = User.objects.all()

    template_data['user'] = user
    template_data['users'] = users
    template_data['url'] = 'users'
    
    return render_to_response('users.html', template_data)

# Contributer Views

@login_required(login_url='/admin/login')
def contributers(request):
    user = request.user
    
    template_data = { }
    
    template_data.update(csrf(request))
    
    try:    
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except Exception as e:
        template_data['allowed'] = False
        
        
    
    
    if request.method == 'POST':
        contributers = []
        if 'search' in request.POST:
            
            template_data['search'] = request.POST['search']
            if 'contributer' in request.POST:
                if len(request.POST['contributer']) > 0:
                    try:
                        contributers = Contributer.objects.filter(pk=int(request.POST['contributer']))
                    except Contributer.DoesNotExist:
                        pass
            
    else:    
        contributers = Contributer.objects.all()
    
    for c in contributers:
        fund_count = len(Fund.objects.filter(contributer = c).filter(active=True))
        c.fund_count = fund_count

    template_data['user'] = user
    template_data['contributers'] = contributers
    template_data['url'] = 'contributers'
    
    return render_to_response('contributers.html', template_data)

@login_required(login_url='/admin/login')
def add_contributer(request):
    template_data = { }
    
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
        template_data['profile'] = profile
    except UserProfile.DoesNotExist:
        pass
    
    try:    
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except Exception as e:
        template_data['allowed'] = False

    
    industries = Industry.objects.all()
    template_data['title'] = 'Add Group'
    template_data['industries'] = industries
    template_data['user'] = user
    template_data['url'] = 'contributers'
    return render_to_response('add_contributer.html', template_data)

@login_required(login_url='/admin/login')
def edit_contributer(request, id = None):
    template_data = { }
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
        template_data['profile'] = profile
    except UserProfile.DoesNotExist:
        pass
    
    
    try:    
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except Exception as e:
        template_data['allowed'] = False
        
    template_data['edit'] = True

    if id != None:
        
        industries = Industry.objects.all()
        template_data['industries'] = industries    
        
        
        try:
            contributer = Contributer.objects.get(pk=int(id))
            template_data['template2'] = AllowedTemplate.objects.filter(contributer=contributer, template_type=2)
            template_data['template3'] = AllowedTemplate.objects.filter(contributer=contributer, template_type=3)
            template_data['contributer'] = contributer
            template_data['title'] = 'Edit Contributer - %s (%d)' % (contributer.name, contributer.id)
            template_data['users'] = contributer.users.all()
        except Contributer.DoesNotExist:
            template_data['contributer'] = None
            
    else:
        pass
    
    template_data['user'] = user
    template_data['url'] = 'contributers'
    return render_to_response('add_contributer.html', template_data)


@login_required(login_url='/admin/login')
def download(request, id = None, year = None, month = None):
    user = request.user
    errors = []
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    # TODO ADD DATE RESTRICTION
    date_parts = current_date.split('-')
    template_data = { }
    
    if year == date_parts[0] and month == date_parts[1]:
        if int(date_parts[2]) < 15:
            errors.append('Cannot download data yet')
        elif int(date_parts[2]) == 15:
            
            weekends = ['Saturday', 'Sunday']
            if datetime.datetime.now().strftime('%A') in weekends:
                errors.append('Data not available yet, please wait till the next available business day')
                
    
    if id != None and year != None and month != None:
        try:
            profile = UserProfile.objects.get(user=user)
            
            try:
                report = Reports.objects.get(id=id)
            
                if profile.user_type.type != 'admin' and profile.user_type.type != 'contributer':
                    try:                        
                        transactions = Transaction.objects.filter(user=user, expires__gt=current_date, valid=True)
                        if report not in profile.reports.all():
                            errors.append('You do not have permission to view this report')
                        
                        report_check = False
                        for t in transactions:
                            if report in t.package.reports.all():
                                report_check = True
                        
                        if report_check == False:
                            errors.append('Report not purchased')
                                                    
                    except Transaction.DoesNotExist:
                        errors.append('No Valid Transactions purchased')                        
            except Reports.DoesNotExist:
                errors.append('Report does not exist')

            
            if len(errors) == 0:
                
                file_path = '%s/timeseries/%s/%s-%s %s.%s' % (settings.MEDIA_ROOT, report.id, year, month, report.name, report.file_type)
                
                download_file = '%s-%s %s.%s' % (year, month, report.name.replace(',',''), report.file_type)

                if os.path.isfile(file_path):
                    report_data = open(file_path, "rb").read()
                    if report.file_type == 'pdf':
                        response =  HttpResponse(report_data, mimetype='application/pdf')
                        
                    if report.file_type == 'xls':
                        response =  HttpResponse(report_data, mimetype='application/vnd.ms-excel')    
                    
                    if report.file_type == 'ppt':
                        response =  HttpResponse(report_data, mimetype='application/vnd.ms-powerpoint')    

                    response['Content-Disposition'] = 'attachment; filename=%s' % download_file
                    return response
                else:
                    errors.append('File does not exist')
                    template_data['errors'] = errors
                    return render_to_response('download_error.html', template_data) 
            else:
                template_data['errors'] = errors
                return render_to_response('download_error.html', template_data)
        except UserProfile.DoesNotExist:
            errors.append('Profile does not exist')
    else:
        errors.append('Not enough data for download')
        template_data['errors'] = errors
        template_data['file_path'] = file_path
        return render_to_response('download_error.html', template_data)
    


@login_required(login_url='/admin/login')
def funds(request, offset = 0, order = 'fund', asc = 'desc'):
    
    offset = int(offset)
    
    user = request.user
    template_data = { }
    template_data.update(csrf(request))
    
    per_page = 10
    max_pages = 5
    pages = 0
    pagination = []
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except:
        template_data['allowed'] = False    
    
    if order == 'fund':
        if asc == 'asc':
            order_by = 'name'
        else:
            order_by = '-name' 
    else:
        if asc == 'asc':
            order_by = 'contributer__name'
        else:
            order_by = '-contributer__name'
    
    
    if request.method == 'POST':
        funds = []
        template_data['search'] = request.POST['search']
        if 'contributer' in request.POST:
            funds = Fund.objects.filter(contributer=request.POST['contributer']).order_by(order_by)
    else:
        funds = Fund.objects.all().order_by(order_by)[(offset*per_page):(offset*per_page)+per_page] 
        pages = math.ceil(float((len(Fund.objects.all())-1)) / float(per_page))
        if pages == 1:
            pages = 0
    
    if 'contributer' not in request.POST:
        if offset != 0:
            page = {}
            page['name'] = 'Previous'
            page['index'] = offset-1
            pagination.append(page)
            
        index = offset - max_pages
        for i in range(offset - max_pages, offset + max_pages):
            if index >= 0 and index <= pages:
                page = {}
                page['name'] = i
                page['index'] = index
                pagination.append(page)
            index = index + 1
            
        if offset != pages:
            page = {}
            page['name'] = 'Next'
            page['index'] = offset+1
            pagination.append(page)
        
    template_data['pagination'] = pagination
    template_data['offset'] = offset
    template_data['order'] = order
    template_data['asc'] = asc
    template_data['funds'] = funds    
    template_data['user'] = user
    template_data['url'] = 'funds'
    
    return render_to_response('funds.html', template_data)

@login_required(login_url='/admin/login')
def add_fund(request):
    user = request.user
    template_data = { }
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except:
        template_data['allowed'] = False
    
    template_data.update(csrf(request))
    template_data['title'] = 'Add Fund'
    template_data['classifications'] = FundClassification.objects.all()
    template_data['company_types'] = CompanyType.objects.all()
    template_data['default_date'] = datetime.datetime.now().strftime('%Y-%m-%d')    
    template_data['fund_categories'] = FundCategory.objects.all()
    template_data['fund_types'] = FundType.objects.all()
    template_data['investment_types'] = InvestmentType.objects.all()
    template_data['sales_fees'] = Fund.SALES_FEE_CHOICES
    
    errors = []
    
    # Create fund
    if request.method == 'POST':
        fund = Fund()
        template_data['request_post'] = request.POST
        
        if 'active' in request.POST:
            if int(request.POST['active']) == 1:
                fund.active = True
            else:
                fund.active = False
        
        if 'classification' in request.POST:
            try:
                classification = FundClassification.objects.get(pk=int(request.POST['classification']))
                fund.classification = classification
            except FundClassification.DoesNotExist:
                errors.append('Fund classification does not exist')
        else:
            errors.append('Fund classification required')
        
        if 'company_type' in request.POST:
            try:
                company_type = CompanyType.objects.get(pk=int(request.POST['company_type']))
                fund.company_type = company_type
            except CompanyType.DoesNotExist:
                errors.append('Company struture does not exist')
        else:
            errors.append('Company structure required')
    
        
        if 'contributer' in request.POST:
            try:
                contributer = Contributer.objects.get(pk=int(request.POST['contributer']))
                fund.contributer = contributer
            except Contributer.DoesNotExist:
                errors.append('Company does not exist')
        else:
            errors.append('No company provided')
            

        if 'fund_category' in request.POST:
            try:
                fund_category = FundCategory.objects.get(pk=int(request.POST['fund_category']))
                fund.category = fund_category
            except FundCategory.DoesNotExist:
                errors.append('Fund category does not exist')
        else:
            errors.append('Fund category is required')
        
        if 'fund_code' in request.POST:
            if len(request.POST['fund_code']) == 3:
                fund.code = request.POST['fund_code']
            else:
                errors.append('Invalid fund code')
        else:
            errors.append('Unique fund code required') 
            

        if 'fund_name' in request.POST:
            fund.name = request.POST['fund_name']
        else:
            errors.append('Please provide a fund name')
            
            
        if 'fund_type' in request.POST:
            try:
                fund_type = FundType.objects.get(pk=int(request.POST['fund_type']))
                fund.type = fund_type
            except FundType.DoesNotExist:
                errors.append('Fund type does not exist')
        else:
            errors.append('Fund type is required')
        
        if 'registration_date' in request.POST:
            try:
                time.strptime(request.POST['registration_date'], '%Y-%m-%d')
                fund.registration_date = request.POST['registration_date']
               
            except ValueError:
               errors.append('Invalid date format')
        else:
            errors.append('Registration date required')
            

        if 'sales_fee' in request.POST:
            sales_fee_check = False
            
            if len(request.POST['sales_fee']) == 3:
                for sales_fee in Fund.SALES_FEE_CHOICES:
                    if sales_fee[0] == request.POST['sales_fee']:
                        sales_fee_check = True
                        
                if sales_fee_check == True:
                    fund.sales_fee = request.POST['sales_fee']
                else:
                    errors.append('Invalid sales fee code')
                                    
            else:
                errors.append('Invalid sales fee')
        else:
            error.append('Sales fee code required')        
        
        if 'hide' in request.POST:
            if int(request.POST['hide']) == 1:
                fund.hide = True
            else:
                fund.hide = False
           
        if 'index' in request.POST:
            if int(request.POST['index']) == 1:
                fund.index = True
            else:
                fund.index = False
        else:
            errors.append('Is the fund indexed')
            
        if 'rrsp' in request.POST:
            if int(request.POST['rrsp']) == 1:
                fund.rrsp = True
            else:
                fund.rrsp = False
        else:
            errors.append('Is the fund rrsp eligible')
    
    
        if 'comments' in request.POST and len(request.POST['comments']) > 0:
            fund.comments = request.POST['comments']
            
        if 'investment_type' in request.POST:
            try:
                investment_type = InvestmentType.objects.get(pk=int(request.POST['investment_type']))
                fund.investment_type = investment_type
            except InvestmentType.DoesNotExist:
                errors.append('Investment type does not exist')
        else:
            errors.append('Investment type required')
                
        try:
            fund.validate_unique()
        except ValidationError:
            errors.append('Fund name / Code must be unique')
                     
        if len(errors) == 0:
            try:
                fund.save()
                if 'funds[]' in request.POST:    
                    fund_list = request.POST['funds[]'].split(',')
                    if len(fund_list) > 0:
                        for f in fund_list:
                            try:
                                if len(f) > 0:
                                    rfund = Fund.objects.get(pk=int(f))
                                    fund.funds.add(rfund)
                            except:
                                errors.append('Could not add fund to fund because Fund does not exist')
                
                
                template_data['action'] = 'Fund Added'
                template_data['request_post'] = { }
            except Exception as e:
                errors.append('Could not create fund: %s' % e)

            
        template_data['errors'] = errors
            
    template_data['user'] = user  
    template_data['url'] = 'funds'
    return render_to_response('add_fund.html', template_data)

@login_required(login_url='/admin/login')
def add_package(request):
    template_data = { }
    errors = []
    
    user = request.user
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except:
        template_data['allowed'] = False
    
    template_data.update(csrf(request))
    template_data['added'] = False
    template_data['request'] = request
    template_data['title'] = 'Add Package'
    reports =  Reports.objects.all()
    
    template_data['reports'] = reports
    attached_reports = []
    if request.method == 'POST':
        for r in reports:
            if '%s' % r.id in request.POST:
                attached_reports.append(r.id)
        
        template_data['attached_reports'] = attached_reports
        
        if 'package_name' in request.POST:
            if len(request.POST['package_name'].strip()) <= 0:
                errors.append('Invalid package name')
        else:
            errors.append('Please provide a package name')
    
        if 'package_description' in request.POST:
            if len(request.POST['package_description'].strip()) <= 0:
                errors.append('Invalid package description')
        else:
            errors.append('Please provide a package description')
            
        if 'package_annual_price' in request.POST:
            if len(request.POST['package_annual_price'].strip()) <= 0:
                errors.append('Invalid annual price')
            else:
                if request.POST['package_annual_price'] and float(request.POST['package_annual_price']) < 0:
                    errors.append('Invalid annual price')
        else:
            errors.append('Please provide a annual price for the package')
    
        if 'package_per_file_price' in request.POST:
            if len(request.POST['package_per_file_price'].strip()) > 0:
                if float(request.POST['package_per_file_price'].strip()) <= 0:
                    errors.append('Invalid per file price')
        
        
        if len(errors) == 0:
            new_package = Package()
            new_package.name = request.POST['package_name']
            new_package.description = request.POST['package_description']
            new_package.price = float(request.POST['package_annual_price'])
            if request.POST['package_per_file_price']:
                new_package.per_file_price = float(request.POST['package_per_file_price'])
            
            if 'pay_period' in request.POST:
                if int(request.POST['pay_period']) == 1:
                    new_package.monthly = True
                if int(request.POST['pay_period']) == 2:
                    new_package.quarterly = True
            
            try:
                new_package.save()

                
                for report in reports:
                    key = '%d' % report.id
                    if key in request.POST:
                        if int(request.POST[key]) == 1:
                            new_package.reports.add(report)

                template_data['added'] = True
                
            except Exception as e:
                errors.append('Could not add package at this time')
                
        template_data['errors'] = errors
        
    template_data['user'] = user
    template_data['url'] = 'packages'
    return render_to_response('add_package.html', template_data)

@login_required(login_url='/admin/login')
def add_user(request):
    template_data = { }
    errors = [] 
    
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        errors.append('No user profile for logged in user')
        
        
    reports = Reports.objects.all()
    attached_reports = [] 
    template_data['current_profile'] = profile
    template_data.update(csrf(request))
    template_data['reports'] = reports
    
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except Exception as e:
        template_data['allowed'] = False    
    
    if template_data['allowed']:
        user_types = UserType.objects.all()
        template_data['user_types'] = user_types
        try:
            if request.method == 'POST':
                for r in reports:
                    if '%s' % r.id in request.POST:
                        attached_reports.append(r.id)
        
                template_data['attached_reports'] = attached_reports
                
                if'username' in request.POST:
                    if len(request.POST['username']) > 0:
                        try:
                            User.objects.get(username=request.POST['username'])
                            errors.append('Username already exists')
                        except User.DoesNotExist:
                            pass
                    else:
                        errors.append('Invalid username')
                else:
                    errors.append('Please provide a username')
                
                if 'email' in request.POST:
                    if len(request.POST['email']) <= 0:
                        errors.append('Invalid email address')
                
               
                
                user_type = None   
                if 'user_type' in request.POST:
                    try:
                        user_type = UserType.objects.get(pk=int(request.POST['user_type']))
                    except UserType.DoesNotExist:
                        errors.append('User type does not exist')
                else:
                    errors.append('Please provide a user type')
                    
                if 'password' in request.POST and 'password_confirm' in request.POST:
                    if len(request.POST['password']) > 0:
                        if request.POST['password'] == request.POST['password_confirm']:
                            new_user = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
                        else:
                            errors.append('Passwords do not match')
                    else:
                        errors.append('Invalid password')
                else:
                    errors.append('Please provide a password')
                
                
                template_data['user_added'] = False
                if len(errors) == 0:
                    try:
                        new_user_profile = UserProfile()
                        new_user_profile.user = new_user
                        new_user_profile.user_type = user_type
                        
                        if 'member' in request.POST:
                            if int(request.POST['member']) == 1:
                                new_user_profile.member = True
                            else:
                                new_user_profile.member = False
                        else:
                            new_user_profile.member = False

                        if 'suppressed' in request.POST:
                            if int(request.POST['suppressed']) == 1:
                                new_user_profile.suppressed = True
                            else:
                                new_user_profile.suppressed = False
                        else:
                            new_user_profile.suppressed = False       
                        
                        if 'active' in request.POST:
                            if int(request.POST['active']) == 1:
                                new_user.is_active = True
                        else:
                            new_user.is_active = False
                        
                        new_user.save()
                        new_user_profile.save()
                        for report in reports:
                            key = '%d' % report.id
                            if key in request.POST:
                                if int(request.POST[key]) == 1:
                                        new_user_profile.reports.add(report)
                        
                        template_data['user_added'] = True
                    except:
                        errors.append('Could not create user')
        except:
            pass
        
    template_data['errors'] = errors
    template_data['user'] = user
    template_data['url'] = 'users'
    return render_to_response('add_user.html', template_data)

def consumer_signup(request):
    template_data = { }
    errors = []
    
    user = request.user
    
    template_data['consumer'] = True
    template_data.update(csrf(request))
    
    #list = mailchimp.utils.get_connection().get_list_by_id('bd2dbc98fc')
    
    # Add user
    if request.method == 'POST':
        if 'username' in request.POST:
            if len(request.POST['username']) <= 0:
                errors.append('Invalid username')
            else:
                try:
                    User.objects.get(username=request.POST['username'])
                    errors.append('Username already exists')
                except User.DoesNotExist:
                    pass
                
        else:
            errors.append('Please provide a user name')
            
        if 'first_name' in request.POST:
            if len(request.POST['first_name']) <= 0:
                errors.append('Invalid first name')
        else:
            errors.append('Please provde a first name')
        
        if 'last_name' in request.POST:
            if len(request.POST['last_name']) <= 0:
                errors.append('Invalid last name')
        else:
            errors.append('Please provide a last name')
            
        
        if 'company' in request.POST:
            if len(request.POST['company']) <= 0:
                errors.append('Invalid company')
        else:
            errors.append('Please provide a company')
        
        
        if 'department' in request.POST:
            if len(request.POST['department']) <= 0:
                errors.append('Invalid department')
        else:
            errors.append('Please provide a department')
                
        if 'position' in request.POST:
            if len(request.POST['position']) <= 0:
                errors.append('Invalid position')
        else:
            errors.append('Please provide a position')
            
        if 'email' in request.POST:
            if len(request.POST['email']) > 0:
                if not email_re.match(request.POST['email']):
                    errors.append('Invaid email')
            else:
                errors.append('Invalid email')   
        else:
            errors.append('Please provide an email')
            
        if 'phone' in request.POST:
            if len(request.POST['phone']) <= 0:
                errors.append('Invalid phone number')
        else:
            errors.append('Please provide a phone number')
        
        if 'password' in request.POST:
            if len(request.POST['password']) > 0:
                if 'confirm_password' in request.POST:
                    if request.POST['password'] != request.POST['confirm_password']:
                        errors.append('Passwords do not match')
                else:
                    errors.append('Please confirm your password')
            else:
                errors.append('Invalid password')
        else:
            errors.append('Please provide a password')
        
        if len(errors) == 0:
            try:
                new_user = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
                if 'first_name' in request.POST:
                    new_user.first_name = request.POST['first_name']
                if 'last_name' in request.POST:
                    new_user.last_name = request.POST['last_name']
                customer_type = UserType.objects.get(type='subscriber')
                user_profile = UserProfile()
                user_profile.user = new_user
                user_profile.user_type = customer_type
                user_profile.department = request.POST['department']
                user_profile.company = request.POST['company']
                user_profile.phone = request.POST['phone']
                user_profile.position = request.POST['position']
                if 'ext' in request.POST:
                    if len(request.POST['ext']) > 0:
                        user_profile.extension = request.POST['ext']
                new_user.save()
                user_profile.save()

                # @TODO: Change this to post email
                try:
                    email_data = { }
                    email_data['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
                    email_data['user'] = new_user
                    email_data['profile'] = user_profile
                    email_data['password'] = request.POST['password']
                    email_data['user_profile'] = user_profile

                    send_email(['statistics@ific.ca'], 'no-reply@ific.ca', email_data, 'consumer_confirmation_email.html', 'IFIC Consumer Signup')
                    # @TODO: Change email this is sent to
                    send_email([new_user.email], 'no-reply@ific.ca', email_data, 'consumer_confirmation_email.html', 'IFIC Consumer Signup')
                except Exception as e:
                    errors.append('Could not send confirmation emails')
                    
                template_data['user_created'] = True
            
                return HttpResponseRedirect("/")
                
            except Exception as e:
                errors.append('Could not create user at this time')
        
        
        template_data['request'] = request    
        template_data['errors'] = errors
    template_data['user'] = user
    
    return render_to_response('signup_consumer.html', template_data)    
    
@login_required(login_url='/admin/login')
def delete_fund(request, id=None):

    user = request.user
    try:
    
        allowed = check_user_permissions(user, ['admin'])
    except Exception as e:
        allowed = False
        
    if allowed:
        try:
            Fund.objects.get(pk=id).delete()
            return HttpResponseRedirect('/admin/funds')  
            
            
        except Fund.DoesNotExist:
            pass

@login_required(login_url='/admin/login')
def edit_fund(request, id=None):
    template_data = { }
    
    user = request.user
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except Exception as e:
        template_data['allowed'] = False
        
    template_data.update(csrf(request))
    template_data['edit'] = True
    
    
    template_data['classifications'] = FundClassification.objects.all()
    template_data['company_types'] = CompanyType.objects.all()
    template_data['default_date'] = datetime.datetime.now().strftime('%Y-%m-%d')    
    template_data['fund_categories'] = FundCategory.objects.all()
    template_data['fund_types'] = FundType.objects.all()
    template_data['investment_types'] = InvestmentType.objects.all()
    template_data['sales_fees'] = Fund.SALES_FEE_CHOICES
    template_data['related'] = False
    
    if id != None:
        try:
            fund = Fund.objects.get(pk=id)      
            related = fund.fund_set.all()
            if len(related) > 0:
                template_data['related'] = True
            template_data['registration_date'] = fund.registration_date.strftime('%Y-%m-%d')
                            
            if request.method == 'POST':
                errors = []
                if 'fund_name' in request.POST and len(request.POST['fund_name']) > 0:
                    fund.name = request.POST['fund_name']
                else:
                    errors.append('Fund name not provided')
                
                if 'fund_code' in request.POST and len(request.POST['fund_code']) <= 3:
                    fund.code = request.POST['fund_code']
                else:
                    errors.append('Invalid fund code')
            
            
                if 'registration_date' in request.POST:
                    fund.registration_date = request.POST['registration_date']
            
                if 'active' in request.POST:
                    if int(request.POST['active']) == 1:
                        fund.active = True
                    else:
                    
                        if fund.investment_type.fund_of_fund == False:
                            if len(related) > 0:
                                for r in related:
                                    r.funds.remove(fund)
                            fund.active = False    
                        else:
                            # @TODO Not clearing relationship
                            try:
                                fund.funds.clear()
                            except Exception as e:
                                pass
                                
                            fund.active = False
                    
                if 'comments' in request.POST:
                    fund.comments = request.POST['comments']
                
                if 'hide' in request.POST:
                    if int(request.POST['hide']) == 1:
                        fund.hide = True
                    else:
                        fund.hide = False
                    
                if 'index' in request.POST:
                    if int(request.POST['index']) == 1:
                        fund.index = True
                    else:
                        fund.index = False
                
                if 'rrsp' in request.POST:
                    if int(request.POST['rrsp']) == 1:
                        fund.rrsp = True
                    else:
                        fund.rrsp = False
                        
                if 'fund_type' in request.POST:
                    try:
                        fund_type = FundType.objects.get(pk=int(request.POST['fund_type']))
                        fund.type = fund_type
                    except FundType.DoesNotExist:
                        errors.append('Invalid fund type')
                else:
                    errors.append('Fund type not provided')
                    
                if 'fund_category' in request.POST:
                    try:
                        fund_category = FundCategory.objects.get(pk=int(request.POST['fund_category']))
                        fund.category = fund_category
                    except FundCategory.DoesNotExist:
                        errors.append('Fund category does not exist')
                else:
                    errors.append('Fund category not provided')
                    
                if 'classification' in request.POST:    
                    try:
                        classification = FundClassification.objects.get(pk=int(request.POST['classification']))
                        fund.classification = classification
                    except FundClassification.DoesNotExist:
                        errors.append('Classification does not eist')
                else:
                    errors.append('Classification not provided')
                    
                if 'sales_fee' in request.POST:
                    for s in Fund.SALES_FEE_CHOICES:
                        if s[0] == request.POST['sales_fee']:
                            fund.sales_fee = request.POST['sales_fee']
                            break
                else:
                    errors.append('Sales fee not provided')
                
                if 'investment_type' in request.POST:
                    try:
                        investment_type = InvestmentType.objects.get(pk=int(request.POST['investment_type']))
                        fund.investment_type = investment_type
                    except InvestmentType.DoesNoeExist:
                        errors.append('Investment type does not exist')
                else:
                    errors.append('Investment type not provided')
                
                        
                if len(errors) == 0:
                    fund.funds.clear()
                    if 'funds[]' in request.POST:
                        fund_list = request.POST['funds[]'].split(',')
                        for f in fund_list:
                            try:
                                if f:
                                    rfund = Fund.objects.get(pk=int(f))
                                    fund.funds.add(rfund)
                            except:
                                errors.append('Could not add fund to fund because Fund does not exist')    
                        
                if len(errors) == 0:
                    fund.save()
                    
                template_data['errors'] = errors
            
                        
            template_data['registration_date'] = fund.registration_date
            template_data['fund'] = fund   
                    
        except Fund.DoesNotExist:
            template_data['fund'] = None
            
        template_data['user'] = user
        
    template_data['url'] = 'funds'
    return render_to_response('add_fund.html', template_data)

@login_required(login_url='/admin/login')
def edit_package(request, id=None):
    template_data = { }
    errors = []
    
    user = request.user
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
        
    except Exception as e:
        template_data['allowed'] = False
    
    template_data['edit'] = True
    template_data.update(csrf(request))
    template_data['added'] = False
    template_data['request'] = request
    template_data['title'] = 'Edit Package'
    
    reports = Reports.objects.all()
    template_data['reports'] = reports
    if id != None:
        try:
            package = Package.objects.get(id=int(id))
            template_data['attached_reports'] = package.reports.all()
    
        except Package.DoesNotExist:
            errors.append('Package does not exist')
    
        if request.method == 'POST':
            if 'package_name' in request.POST:
                if len(request.POST['package_name'].strip()) <= 0:
                    errors.append('Invalid package name')
                else:
                    package.name = request.POST['package_name']
            else:
                errors.append('Please provide a package name')
        
            if 'package_description' in request.POST:
                if len(request.POST['package_description'].strip()) <= 0:
                    errors.append('Invalid package description')
                else:
                    package.description = request.POST['package_description']
            else:
                errors.append('Please provide a package description')
                
            if 'package_annual_price' in request.POST:
                if len(request.POST['package_annual_price'].strip()) <= 0:
                    errors.append('Invalid annual price')
                else:
                    if request.POST['package_annual_price'] and float(request.POST['package_annual_price']) < 0:
                        errors.append('Invalid annual price')
                    else:
                        package.price = float(request.POST['package_annual_price'])
            else:
                errors.append('Please provide a annual price for the package')
        
            if 'package_per_file_price' in request.POST:
                if len(request.POST['package_per_file_price'].strip()) > 0:
                    if float(request.POST['package_per_file_price'].strip()) <= 0:
                        errors.append('Invalid per file price')
                    else:
                        package.per_file_price = float(request.POST['package_per_file_price'])
            
            if 'pay_period' in request.POST:
                if int(request.POST['pay_period']) == 1:
                    package.monthly = True
                    package.quarterly = False
                if int(request.POST['pay_period']) == 2:
                    package.quarterly = True
                    package.monthly = False
            
            if len(errors) == 0:
                package.reports.clear()
                try:
                    package.save()
                    for report in reports:
                        key = '%d' % report.id
                        if key in request.POST:
                            if int(request.POST[key]) == 1:
                                package.reports.add(report)
                    
                    template_data['added'] = True
                except:
                    errors.append('Could not add package at this time')
                        
    template_data['package'] = package
    template_data['errors'] = errors
    template_data['user'] = user
    template_data['url'] = 'packages'
    return render_to_response('add_package.html', template_data)        

@login_required(login_url='/admin/login')
def edit_user(request, id = None):
    template_data = { }
    errors = [] 
    user = request.user

    try:
        template_data['allowed'] = check_user_permissions(user, ['admin', 'contributer', 'subscriber', 'customer'])
    except Exception as e:
        template_data['allowed'] = False
    
    try:
        current_user_profile = UserProfile.objects.get(user=user)
        template_data['current_profile'] = current_user_profile
    except Profile.DoesNotExist:
        errors.append('Profile does not exist') 
    
    template_data.update(csrf(request))
    template_data['edit'] = True
    template_data['profile'] = None
    user_types = UserType.objects.all()
    template_data['user_types'] = user_types
    
    if id == None:
        id = user.id
    
    reports = Reports.objects.all()
    template_data['reports'] = reports         
    if id != None:
        try:
            edit_user = User.objects.get(pk=id)
            profile = UserProfile.objects.get(user=edit_user)
            template_data['attached_reports'] = profile.reports.all()
            
            # Save user
            if request.method == 'POST':
                try:        
                    if 'username' in request.POST:
                        edit_user.username = request.POST['username']
                    
                    if 'email' in request.POST:
                        edit_user.email = request.POST['email']
                    
                    if 'password' in request.POST:
                        if len(request.POST['password']) > 0:
                            if request.POST['password'] == request.POST['password_confirm']:
                                edit_user.set_password(request.POST['password'])
                            else:
                                errors.append('Passwords do not match')

                    if current_user_profile.user_type.type == 'admin':           
                        if 'member' in request.POST:
                            if int(request.POST['member']) == 1:
                                profile.member = True 
                        else:
                            profile.member = False
                            
                        if 'suppressed' in request.POST:
                            if int(request.POST['suppressed']) == 1:
                                profile.suppressed = True
                            else:
                                profile.suppressed = False
                        else:
                            profile.suppressed = False
                    
                        if 'active' in request.POST:
                            if int(request.POST['active']) == 1:
                                edit_user.is_active = True
                            else:
                                edit_user.is_active = False
                        else:
                            edit_user.is_active = False
                    
                    if 'user_type' in request.POST:
                        try:
                            user_type = UserType.objects.get(pk=int(request.POST['user_type']))
                            profile.user_type = user_type
                        except UserType.DoesNotExist:
                            errors.append('User type does not exist')
                             
                        # @TODO: Customer specific
                        if user_type.type == 'customer':
                            if 'permission' in request.POST:
                                profile.permission = int(request.POST['permission'])
                            
                    
                    if len(errors) == 0:
                        try:
                            edit_user.save()
                            profile.save()
                            
                            if current_user_profile.user_type.type == 'admin':
                                profile.reports.clear()
                                for report in reports:
                                    key = '%d' % report.id
                                    if key in request.POST:
                                        if int(request.POST[key]) == 1:
                                            profile.reports.add(report)
                            
                            template_data['user_editted'] = True
                        except Exception:
                            errors.append('Could not save user')
                
                
                except User.DoesNotExist:
                    errors.append('User does not exist')
                except UserProfile.DoesNotExist:
                    profile = UserProfile.objects.create(user=edit_user)
                    profile.user_type = user_type
                    

            template_data['edit_user'] = edit_user
            template_data['profile'] = profile
            template_data['errors'] = errors
                       
        except User.DoesNotExist:
            errors.append('User does not exist')
        except UserProfile.DoesNotExist:
            errors.append('Profile does not exist')
    else:
        errors.append('Invalid user')
        
    template_data['errors'] = errors
    template_data['user'] = user
    template_data['url'] = 'users'
    return render_to_response('add_user.html', template_data)

@login_required(login_url='/admin/login')
def list_management(request, type=None):
    template_data = { }
    list_data = []
    user = request.user
    
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except:
        template_data['allowed'] = False
    
    
    template_data.update(csrf(request))
    
    
    if type != None:
        type = type.lower()
        template_data['type'] = type
            
        if type == 'company':
            if request.method == 'POST':
                if 'company_type' in request.POST:
                    if 'id' in request.POST:
                        if request.POST['id'] and int(request.POST['id']):
                            try:
                                company_type = CompanyType.objects.get(pk=int(request.POST['id']))
                                company_type.name = request.POST['company_type']
                                company_type.save()
                            except CompanyType.DoesNotExist:
                                template_data['error'] = 'Company type does not exist'
                        else: 
                            try:
                                CompanyType.objects.create(name=request.POST['company_type'])
                                template_data['action'] = 'Company Type %s added' % request.POST['company_type']
                            except Exception as e:
                                template_data['error'] = 'Could not create company type'
                else:
                    template_data['error'] = 'Please provide a company type'    
                
            list_data = CompanyType.objects.all()
    
    
        if type == 'fund':
            if request.method == 'POST':
                if 'fund_type' in request.POST and 'fund_code' in request.POST:
                    if 'id' in request.POST:
                        if request.POST['id'] and int(request.POST['id']):
                            try:
                                fund_type = FundType.objects.get(pk=int(request.POST['id']))
                                fund_type.name = request.POST['fund_type']
                                fund_type.save()
                            except FundType.DoesNotExist:
                                template_data['error'] = 'Fund type does not exist'
                        else:
                            try:
                                FundType.objects.create(name=request.POST['fund_type'], code=request.POST['fund_code'].upper())
                                template_data['action'] = 'Fund Type %s added with code %s' % (request.POST['fund_type'], request.POST['fund_code'].upper())
                            except Exception as e:
                                template_data['error'] = 'Could not create fund type'

            list_data = FundType.objects.all()
            
                    
        if type == 'category':
            if request.method == 'POST':
                if 'category_type' in request.POST and 'category_code' in request.POST:
                    if 'id' in request.POST:
                        if request.POST['id'] and int(request.POST['id']):
                            try:
                                category_type = FundCategory.objects.get(pk=int(request.POST['id']))
                                category_type.name = request.POST['category_type']
                                category_type.save()
                            except FundCategory.DoesNotExist:
                                template_data['error'] = 'Fund category does not exist'
                        else:
                            try:
                                FundCategory.objects.create(name=request.POST['category_type'], code=request.POST['category_code'].upper())
                                template_data['action'] = 'Fund Type %s added with code %s' % (request.POST['category_type'], request.POST['category_code'].upper())
                            except IntegrityError:
                                template_data['error'] = 'Code already exists'
                            except Exception as e:
                                template_data['error'] = 'Could not create fund category'    
        
    
      
            list_data = FundCategory.objects.all()
       
        if type == 'industry':
            if request.method == 'POST':
                if 'industry_type' in request.POST and 'industry_code' in request.POST:
                    if 'id' in request.POST:
                        if request.POST['id'] and int(request.POST['id']):
                            try:
                                industry = Industry.objects.get(pk=int(request.POST['id']))
                                industry.name = request.POST['industry_type']
                                industry.save()
                            except Industry.DoesNotExist:
                                template_data['error'] = 'Fund category does not exist'
                        else:
                            try:
                                Industry.objects.create(name=request.POST['industry_type'], code=request.POST['industry_code'].upper())
                                template_data['action'] = 'Industry %s added with code %s' % (request.POST['industry_type'], request.POST['industry_code'].upper())
                            except IntegrityError:
                                template_data['error'] = 'Code already exists'
                            except Exception as e:
                                template_data['error'] = 'Could not create Industry'    
        
    
      
            list_data = Industry.objects.all()
        
        if type == 'classification':
            if request.method == 'POST':
                if 'classification_type' in request.POST:
                     if 'id' in request.POST:
                        if request.POST['id'] and int(request.POST['id']):
                            try:
                                fund_classification = FundClassification.objects.get(pk=int(request.POST['id']))
                                fund_classification.name = request.POST['classification_type']
                                fund_classification.save()
                            except CompanyType.DoesNotExist:
                                template_data['error'] = 'Classification type does not exist'
                        else: 
                            try:
                                FundClassification.objects.create(name=request.POST['classification_type'])
                                template_data['action'] = 'Fund Classification %s added' % request.POST['classification_type']
                            except Exception as e:
                                template_data['error'] = 'Could not create fund classification'    
    
            list_data = FundClassification.objects.all()    
            
            
        if type == 'investment':
            if request.method == 'POST':
                if 'investment_type' in request.POST:
                     if 'id' in request.POST:
                        if request.POST['id'] and int(request.POST['id']):
                            try:
                                investment_type = InvestmentType.objects.get(pk=int(request.POST['id']))
                                investment_type.name = request.POST['investment_type']
                                fund_of_fund = False
                                if 'fund_of_fund' in request.POST:
                                    if int(request.POST['fund_of_fund']) == 1:
                                        fund_of_fund = True
                                    else:
                                        fund_of_fund = False
                                
                                investment_type.fund_of_fund = fund_of_fund
                                
                                if 'company' in request.POST:
                                    for c in InvestmentType.COMPANY_CHOICES:
                                        if c[0] == int(request.POST['company']):
                                            investment_type.company = int(request.POST['company'])
                                            break
                                    
                                
                                if 'can_own' in request.POST:
                                    try:
                                        can_own = None
                                        if int(request.POST['can_own']) != 0:
                                            investment_type.can_own = InvestmentType.objects.get(pk=int(request.POST['can_own']))
                                            investment_type.save()
                                    except InvestmentType.DoesNotExist:
                                        template_data['error'] = 'Investment type does not exist'
                    
                            except InvestmentType.DoesNotExist:
                                template_data['error'] = 'Investment type does not exist'
                        else: 
                            try:

                                          
                                try:
                                    can_own = None
                                    
                                    if 'can_own' in request.POST:
                                        if int(request.POST['can_own']) != 0:
                                            can_own = InvestmentType.objects.get(pk=int(request.POST['can_own']))
                        
                                    try:
                                        
                                        fund_of_fund = False
                                        if 'fund_of_fund' in request.POST:
                                            if int(request.POST['fund_of_fund']) == 1:
                                                fund_of_fund = True
                                            else:
                                                fund_of_fund = False
                                                
                                        company = 0
                                        if 'company' in request.POST:
                                            for c in InvestmentType.COMPANY_CHOICES:
                                                if c[0] == int(request.POST['company']):
                                                    company = int(request.POST['company'])
                                                    break
                                    
                                        InvestmentType.objects.create(name=request.POST['investment_type'], fund_of_fund=fund_of_fund, can_own=can_own, company=company)
                                       
                                                    
                                    except Exception as e:
                                        template_data['error'] = 'Could not create investment type'
                                   
                                except InvestmentType.DoesNotExist:
                                    template_data['error'] = 'Investment type does not exist'
                                    
                                        
                                
                                template_data['action'] = 'Investment type %s added' % request.POST['investment_type']
                            except Exception as e:
                                template_data['error'] = 'Could not create investment type'    
            
            template_data['company_selections'] = InvestmentType.COMPANY_CHOICES
            list_data = InvestmentType.objects.all()
                            
        template_data['list_data'] = list_data
        
    template_data['user'] = user
    template_data['url'] = 'utilities'
    return render_to_response('lists.html', template_data)


# Login Views    

def login(request):
    template_data = { }
    user = request.user
    
    template_data['user'] = user
    template_data['consumer'] = True
    
    return render_to_response('login.html', template_data)

def logout(request):

    auth_logout(request)

    return HttpResponseRedirect("/admin/login")

@login_required(login_url='/admin/login')
def logs(request):
    template_data = { }
    user = request.user
    
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except:
        template_data['allowed'] = False
    
    template_data.update(csrf(request))
    
    if template_data['allowed'] == True:
        user_logs = UserLog.objects.all()
        template_data['user_logs'] = user_logs

    template_data['url'] = 'utilities'
    template_data['user'] = user
    
    return render_to_response('logs.html', template_data)

@login_required(login_url='/admin/login')
def packages(request):
    template_data = { }
    packages = Package.objects.all()
    user = request.user
    
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except:
        template_data['allowed'] = False
    
    template_data.update(csrf(request))
    
    if template_data['allowed'] == True:
        template_data['packages'] = packages
    
    template_data['user'] = user
    template_data['url'] = 'packages'
    return render_to_response('packages.html', template_data) 

@login_required(login_url='/admin/login')
def purchase(request):
    template_data = { }
    errors = []
    user = request.user
    template_data.update(csrf(request))
    
    try:
        profile = UserProfile.objects.get(user=user)
        packages = Package.objects.all()
        template_data['packages'] = packages
        current_year = int(datetime.datetime.now().strftime('%Y'))
        current_month = int(datetime.datetime.now().strftime('%m'))
        
        template_data['current_year'] = current_year
        template_data['current_month'] = current_month
        
        template_data['years'] = range(current_year, current_year + 20)                
        template_data['countries'] = (
                                      ('CA', 'Canada'),
                                      ('US', 'United States of America')                              
        )
        template_data['states'] = STATES

    except UserProfile.DoesNotExist:
        errors.append('User profile not found')
    
    template_data['errors'] = errors
    template_data['user'] = user
    template_data['url'] = 'packages'
    return render_to_response('purchase.html', template_data) 

@login_required(login_url='/admin/login')
def purchase_summary(request):
    
    user = request.user
    errors = []
    template_data = { }
    
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        error.append('Profile does not exist')
    
    template_data['name'] = '%s %s' % (user.first_name, user.last_name)
    template_data['profile'] = profile
    if 'update_transactions' in request.session:
        template_data['update_transactions'] = request.session['update_transactions']
    if 'new_transactions' in request.session:
        template_data['new_transactions'] = request.session['new_transactions']
    
    return render_to_response('purchase_summary.html', template_data)

@login_required(login_url='/admin/login')
def reports(request):
    
    user = request.user
    errors = []
    template_data = { }
    
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except:
        template_data['allowed'] = False
    
    
    reports = Reports.objects.all()
    template_data['reports'] = reports
    
    try:
        setting = UploadSetting.objects.get(pk=1)
        template_data['default_date'] = setting.upload_date.strftime('%Y-%m-%d')
    except UploadSetting.DoesNotExist:
        template_data['default_date'] = datetime.datetime.now().strftime('%Y-%m-%d')
    
    date_parts = template_data['default_date'].split('-')
    reports_uploaded = []
     
    for report in reports:
        file_path = '%s/timeseries/%d/%s-%s %s.%s' % (settings.MEDIA_ROOT, report.id, date_parts[0], date_parts[1], report.name, report.file_type)
        if os.path.isfile(file_path):
            reports_uploaded.append(report)

            
    template_data['reports_uploaded'] = reports_uploaded
    
    sa_report = open_report(0)
    pim_report = open_report(1)
    fav_report = open_report(2)
    
    if sa_report != False:
        template_data['sa_report'] = sa_report[5:]

    if pim_report != False:
        template_data['pim_report'] = pim_report[5:]
        
    if fav_report != False:
        template_data['fav_report'] = fav_report[5:]
    
    if len(errors) > 0:
        template_data['errors'] = errors
    
    template_data['user'] = user
    template_data['url'] = 'reports'
    return render_to_response('reports.html', template_data)

@login_required(login_url='/admin/login')
def stats(request, year = None, month = None):
    template_data = { }
    warnings = []
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except:
        pass
    
    try:
        upload_setting = UploadSetting.objects.get(pk=1)
        default_date = upload_setting.upload_date.strftime('%Y-%m')
        report_view_date = upload_setting.report_view_date.strftime('%Y-%m')
    except UploadSetting.DoesNotExist:
        default_date = datetime.datetime.now().strftime('%Y-%m')
    
    if report_view_date:
        template_data['current_date'] = report_view_date
        if not year:
            year = upload_setting.report_view_date.strftime('%Y')
        if not month:
            month = upload_setting.report_view_date.strftime('%m')
    else:
        template_data['current_date'] = default_date
    
    current_date = None

    if year and month:
        
        try:
            current_date = datetime.datetime.strptime('%d-%d' % (int(year), int(month)), '%Y-%m')
        except Exception as e:
            print e
    else:
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        
           
    template_data['current_date'] = current_date.strftime('%Y-%m')
        
        
    template_data['allowed_reports'] = profile.reports.all()
    
    reports = Reports.objects.all().order_by('quarterly')
    
    transactions = Transaction.objects.filter(user=user, expires__gt=current_date)
    for report in reports:
        file_path = '%s/timeseries/%s/%s-%s %s.%s' % (settings.MEDIA_ROOT, report.id, year, month, report.name, report.file_type)
        
        if os.path.isfile(file_path):
            report.uploaded = True
        else:
            report.uploaded = False
        
        
        
        if 'Quarterly' in report.name:
            report.quarterly = True
        
        if len(transactions) > 0:
            for transaction in transactions:
                if report in transaction.package.reports.all():
                    report.download = True
                    warning_range = datetime.datetime.combine(transaction.expires, datetime.time()) - datetime.timedelta(weeks = 2)     
                    if warning_range < datetime.datetime.now():
                        warnings.append(int(report.id))
    
    
    
    template_data['transactions'] = transactions
    template_data['reports'] = reports
    template_data['user'] = user
    template_data['warnings'] = warnings
    
    
    template_data['profile'] = profile
    template_data['url'] = 'stats'
    template_data['month'] = month
    template_data['year'] = year
    return render_to_response('stats.html', template_data)

@login_required(login_url='/admin/login')
def transactions(request):
    template_data = { }
    template_data.update(csrf(request))
    user = request.user
      
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except:
        template_data['allowed'] = False
    
    if request.method == 'POST':
        if 'transaction' in request.POST:
            template_data['search'] = request.POST['transaction']
            try:
                transactions = Transaction.objects.filter(pk=int(request.POST['transaction']))
            except Transaction.DoesNotExist:
                transactions = []
        else:
            transactions = Transaction.objects.all()
    else:
        transactions = Transaction.objects.all()

    template_data['transaction_types'] = Transaction.TRANSACTION_TYPES
    template_data['transactions'] = transactions
    template_data['url'] = 'utilities'
    template_data['user'] = user

    return render_to_response('transactions.html', template_data)

@login_required(login_url='/admin/login')
def add_transaction(request):
    template_data = { }
    user = request.user
    errors = []
    
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except:
        template_data['allowed'] = False

    
    if template_data['allowed']:
        template_data['transaction_types'] = Transaction.TRANSACTION_TYPES
        template_data['packages'] = Package.objects.all()
        pass
    else:
        pass
    
    return render_to_response('add_transaction.html', template_data)


@login_required(login_url='/admin/login')
def edit_transaction(request, id = None):
    template_data = { }
    user = request.user
    errors = []
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except:
        template_data['allowed'] = False

    
    if template_data['allowed']:
        try:
            transaction = Transaction.objects.get(pk=id)
        except Transaction.DoesNotExist:
            errors.append('Transaction does note exist')
    
        if request.method == 'POST':
            if 'valid' in request.POST:
                if int(request.POST['valid']) == 1:
                    transaction.valid = True
                else:
                    transaction.valid = False
                    
            try:
                transaction.save()
            except Exception:
                errors.append('Could not save transaction')    

    else:
        errors.append('Invalid permissions')
        
      
    template_data['errors'] = errors
    return render_to_response('add_transaction.html', template_data)


@login_required(login_url='/admin/login')
def validation(request):
    template_data = { }
    templates = []
    errors = []
    user = request.user
    
    try:
        upload_setting = UploadSetting.objects.get(pk=1)
        month = upload_setting.upload_date.strftime('%m')
        year = upload_setting.upload_date.strftime('%Y')
        default_date = upload_setting.upload_date.strftime('%Y-%m-%d')
    except UploadSetting.DoesNotExist:
        month = datetime.datetime.now().strftime('%m')
        year = datetime.datetime.now().strftime('%Y')
        default_date = datetime.datetime.now().strftime('%Y-%m-%d')  
    
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        pass
    
    template_data['default_date'] = default_date
    template_data['profile'] = profile
    template_data.update(csrf(request))
    
    if 'stand_alone_view_response' in request.session:
        stand_alone_response = request.session['stand_alone_view_response']
            
        if stand_alone_response.ready():
            template_data['stand_alone_response'] = True
        else:
            if not stand_alone_response.result:
                template_data['stand_alone_generating'] = True
            
            template_data['stand_alone_response'] = False 
       

    if 'primary_investment_response' in request.session:
        primary_investment_response = request.session['primary_investment_response']
                
        if primary_investment_response.ready():
            template_data['primary_investment_response'] = True
        else:
            if not primary_investment_response.result:
                template_data['primary_investment_generating'] = True
            
            template_data['primary_investment_response'] = False    
    
    if 'funds_admin_response' in request.session:
        funds_admin_response = request.session['funds_admin_response']
        
        if funds_admin_response.ready():
            template_data['funds_admin_response'] = True
        else:
            if not funds_admin_response.result:
                template_data['funds_admin_generating'] = True
            
            template_data['funds_admin_response'] = False     
    
    if request.method == 'POST':
        if 'contributer' in request.POST:
            try:
                contributers = Contributer.objects.filter(pk=int(request.POST['contributer']))
            except Contributer.DoesNotExist:
                contributers = []
        else:
            contributers = Contributer.objects.all()
        
        if 'date_range' in request.POST:
            if len(request.POST['date_range'].strip()) == 10:
                default_date = request.POST['date_range']
                date_pieces = request.POST['date_range'].strip().split('-')
                if len(date_pieces[0]) == 4:
                    year = date_pieces[0]
                else:
                    month = datetime.datetime.now().strftime('%m')
                    year = datetime.datetime.now().strftime('%Y')
                if len(date_pieces[1]) == 2:
                    month = date_pieces[1] 
                else:
                    month = datetime.datetime.now().strftime('%m')
                    year = datetime.datetime.now().strftime('%Y')
            else:
                try:
                    setting = UploadSetting.objects.get(pk=1)
                    month = setting.upload_date.strftime('%m')
                    year = setting.upload_date.strftime('%Y')
                except:
                    pass
        else:
            try:
                setting = UploadSetting.objects.get(pk=1)
                month = setting.upload_date.strftime('%m')
                year = setting.upload_date.strftime('%Y')
            except:
                pass
    
    else:
        contributers = Contributer.objects.all()
    

    for contributer in contributers:
        try:
            valid_template = ValidTemplate.objects.get(contributer=contributer, date__year=year, date__month=month)
            if valid_template.template_one == False:
                errors = TemplateError.objects.filter(valid_template=valid_template, template=1)
                valid_template.template_one_errors = errors
            if valid_template.template_two == False:
                errors = TemplateError.objects.filter(valid_template=valid_template, template=2)
                valid_template.template_two_errors = errors
            if valid_template.template_three == False:
                errors = TemplateError.objects.filter(valid_template=valid_template, template=3)
                valid_template.template_three_errors = errors
                    
            templates.append(valid_template)
            
        except ValidTemplate.DoesNotExist:
            valid_template = ValidTemplate()
            valid_template.template_one = False
            valid_template.template_two = False
            valid_template.template_three = False
            valid_template.template_one_errors = []
            valid_template.template_two_errors = []
            valid_template.template_three_errors = []
            
            valid_template.contributer = contributer
            templates.append(valid_template)
    
    template_data['templates'] = templates
    template_data['default_date'] = default_date
    template_data['user'] = user
    template_data['url'] = 'utilities'
    template_data['year'] = year
    template_data['month'] = month
    return render_to_response('validation.html', template_data)
    
@csrf_exempt
def upload_timeseries(request):
    response = { }
    user = request.user
    errors = []
    try:
        allowed = check_user_permissions(user, ['admin'])
    except:
        allowed = False
    
    if allowed == True:
        if 'report' in request.GET:
            try:
                report = Reports.objects.get(pk=int(request.GET['report']))
                if not os.path.isdir('%s/timeseries' % (settings.MEDIA_ROOT)):
                    os.mkdir('%s/timeseries' % (settings.MEDIA_ROOT))
                
                if not os.path.isdir('%s/timeseries/%s' % (settings.MEDIA_ROOT, report.id)):
                    os.mkdir('%s/timeseries/%s' % (settings.MEDIA_ROOT, report.id))
                    
                if 'date' in request.GET:
                    date_parts = request.GET['date'].split('-')
                
                from io import FileIO, BufferedWriter
                file_path = '%s/timeseries/%s/%s-%s %s.%s' % (settings.MEDIA_ROOT, report.id, date_parts[0], date_parts[1], report.name, report.file_type)
                
                try:
                    # For IE
                    if 'qqfile' in request.FILES:
                        destination = open(file_path, 'wb+')
                        data = request.FILES['qqfile']
                        for c in data.chunks():
                            destination.write(c)
                           
                        destination.close()
                    else:
                        with BufferedWriter(FileIO(file_path, "w" )) as dest:
                            foo = request.read(1024)
                            while foo:
                                dest.write(foo)
                                foo = request.read(1024)
                    
                    response['report'] = report.id
                    response['report_name'] = report.name   
                    response['success'] = True
                    
                except Exception as e:
                    errors.append('Could not upload timeseries')  
            except Reports.DoesNotExist:
                errors.append('Report does not exist')
                
        else:
            errors.append('Please select a report to upload')
    else:
        errors.append('Invalid permissions')
    
    if len(errors) > 0:
        response['success'] = False
        response['errors'] = errors
    
    json_response = simplejson.dumps(response)
    return HttpResponse(json_response)   
        
        
@csrf_exempt
def upload_file(request):
    response = { }
    user = request.user
    
    try:
        allowed = check_user_permissions(user, ['admin', 'contributer'])
    except:
        allowed = False
    
    if allowed:
        try:
            template = 0
            if 'template' in request.GET:
                template = int(request.GET['template'])
                
                
                from io import FileIO, BufferedWriter
                upload_dir = '%s/uploads' % (settings.MEDIA_ROOT)
                
                if not os.path.isdir(upload_dir):
                    os.mkdir(upload_dir) 
                
                contributer = None
                if 'contributer' in request.GET:
                    try:
                        contributer = Contributer.objects.get(pk=int(request.GET['contributer']))
                        if not os.path.isdir('%s/%s' % (upload_dir, request.GET['contributer'])):
                            os.mkdir('%s/%s' % (upload_dir, request.GET['contributer']))
                       

                        try:
                            upload_setting = UploadSetting.objects.get(pk=1)
                            current_date = upload_setting.upload_date.strftime('%Y-%m')
                        except UploadSetting.DoesNotExist:
                            current_date = datetime.datetime.now().strftime('%Y-%m')
                        
                        file_path = '%s/%s/%s' % (upload_dir, request.GET['contributer'], '%s_template%d.csv' % (current_date, template))
                        
                        if 'qqfile' in request.FILES:
                            destination = open(file_path, 'wb+')
                            data = request.FILES['qqfile']
                            for c in data.chunks():
                                destination.write(c)
                                
                                
                            destination.close()
                            
                            
                        else:
                            # Write file to system    
                            with BufferedWriter(FileIO(file_path, "w" )) as dest:
                                foo = request.read(1024)
                                while foo:
                                    dest.write(foo)
                                    foo = request.read(1024)
           
                        mime_type = mimetypes.guess_type(file_path, True)
                        
                        if mime_type[0] != 'text/plain' and mime_type[0] != 'text/csv':
                            response['success'] = 'error'
                            response['message'] = 'Invalid file type'
                        
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                            
                        else:
                            response['success'] = 'true'
                            with open(file_path, 'U') as csv_file:   
                                template_data = list(csv.reader(csv_file, dialect='excel-tab'))
                                
                            for row in template_data:
                                for column in row:
                                    column = column.replace('\"', '')
                            
                            try:
                                validation = ValidTemplate.objects.get(contributer=contributer, date__year=upload_setting.upload_date.strftime('%Y'), date__month=upload_setting.upload_date.strftime('%m'))
                                validation.date = upload_setting.upload_date.strftime('%Y-%m-%d')
                            except ValidTemplate.DoesNotExist:
                                validation = ValidTemplate(contributer=contributer, date=upload_setting.upload_date.strftime('%Y-%m-%d'))
                                
                            validation.save()
                            
                    except Contributer.DoesNotExist:
                        response['success'] = 'error'
                        response['message'] = 'Group does not exist' 
                
                else:
                    response['success'] = 'error'
                    response['message'] = 'Could not upload file no group provided'
            else:
                response['success'] = 'error'
                respnse['message'] = 'Invalid template'                                   
        except Exception as e:
            response['success'] = 'error'
            response['message'] = '%s' % e
    else:
        response['success'] = 'error'
        response['message'] = 'Invalid permissions'
    

    json_response = simplejson.dumps(response)
    return HttpResponse(json_response)       

@login_required(login_url='/admin/login')         
def upload(request):
    template_data = { }
    user = request.user
    
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin', 'contributer'])
    except:
        template_data['allowed'] = False

    template_data.update(csrf(request))
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        pass

    template_data['profile'] = profile

    if 'step' in request.session:
        step = int(request.session['step'])
    else:
        step = 0
        
    try:
        upload_setting = UploadSetting.objects.get(pk=1)
        template_data['upload_month'] = upload_setting.upload_date.strftime('%Y-%m')
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')

        if profile.user_type.type != 'admin':
            if current_date >= upload_setting.stop_upload_date.strftime('%Y-%m-%d'):
                template_data['can_upload'] = False
            else:
                template_data['can_upload'] = True
        else: 
            template_data['can_upload'] = True            

    except UploadSetting.DoesNotExist:
        pass

    template_data['step'] = step    

    contributer = None
    template2_present = False
    template3_present = False

    if 'contributer' in request.session:
        contributer = request.session['contributer']
        template_data['contributer'] = contributer

        funds_check = Fund.objects.filter(contributer=contributer)
        for f in funds_check:
            if f.investment_type.id == 2:
                template2_present = True
                
            if f.investment_type.id == 3:
                template3_present = True

            if f.investment_type.id == 4:
                template2_present = True
                template3_present = True
        
    template_data['template2_present'] = template2_present
    template_data['template3_present'] = template3_present

    if step == 1:

        templates= []

        templates.append((1, 'Template 1'))
        templates.append((2, 'Template 2'))
        templates.append((3, 'Template 3'))

        template_data['templates'] = templates
        path = '%s/uploads/%d' % (settings.MEDIA_ROOT, contributer.id)

        try:
            upload_setting = UploadSetting.objects.get(pk=1)
            current_date = upload_setting.upload_date.strftime('%Y-%m')
        except UploadSetting.DoesNotExist:
            current_date = datetime.datetime.now().strftime('%Y-%m')

            
        templates_have = []
        templates_false = []
        templates_uploaded = []

        # Everyone has template 1
        templates_have.append((1, 'Template 1'))

        if Fund.objects.filter(contributer=contributer, investment_type=InvestmentType(pk=3)).count() > 0:
            templates_have.append((2, 'Template 2'))
        else:
            if Fund.objects.filter(contributer=contributer, investment_type=InvestmentType(pk=4)).count() > 0:
                templates_have.append((2, 'Template 2'))

        if Fund.objects.filter(contributer=contributer, investment_type=InvestmentType(pk=2)).count() > 0:
            templates_have.append((3, 'Template 3'))

        try:
            template_1 = False
            template_2 = False
            template_3 = False

            if os.path.isdir(path): 
                for file in os.listdir(path):
                    file = file.split('_')

                    if file[0] == current_date:
                        file = file[1].split('.')

                        if file[0] == 'template1':
                            template_1 = True
                            templates_uploaded.append((1, 'Template 1'))

                        if file[0] == 'template2':
                            template_2 = True
                            templates_uploaded.append((2, 'Template 2'))

                        if file[0] == 'template3':      
                            templates_uploaded.append((3, 'Template 3'))               
                            template_3 = True


            if template_1 == False:
                templates_false.append((1, 'Template 1'))

            if template_2 == False:
                templates_false.append((2, 'Template 2'))

            if template_3 == False:
                templates_false.append((3, 'Template 3'))
                
            template_data['templates_uploaded'] = templates_uploaded
            template_data['templates_have'] = templates_have
            template_data['templates_false'] = templates_false
        except:
            pass

    

    template_data.update(csrf(request))

    template_data['user'] = user

    template_data['url'] = 'upload'

    return render_to_response('upload_data.html', template_data)

@login_required(login_url='/admin/login')  
def upload_settings(request):
    template_data = { }
    user = request.user
    
    try:
        template_data['allowed'] = check_user_permissions(user, ['admin'])
    except:
        template_data['allowed'] = False
        
    template_data.update(csrf(request))
    
    if template_data['allowed']:
        try:
            upload_setting = UploadSetting.objects.get(pk=1)
            if upload_setting.upload_date:
                template_data['upload_month'] = upload_setting.upload_date.strftime('%Y-%m-%d')
            if upload_setting.stop_upload_date:
                template_data['cutoff_date'] = upload_setting.stop_upload_date.strftime('%Y-%m-%d')
            if upload_setting.report_view_date:
                template_data['report_view_date'] = upload_setting.report_view_date.strftime('%Y-%m-%d')
        except UploadSetting.DoesNotExist:
            pass
        
    template_data['user'] = user
    
    return render_to_response('upload_settings.html', template_data)

def send_email(to_email, from_email, template_data, template_file, title):
    
    try:
        message = render_to_string(template_file, template_data)
        
        send_mail(title, message, from_email, to_email, fail_silently=False)
    except Exception as e:
        raise Exception('Could not send email')

def open_report(template, date = None):
    
    template_data = { }
    
    reports = [ 'stand_alone_view', 'primary_investment_management' , 'funds_administration_view']
    
    if date == None:
        try:
            setting = UploadSetting.objects.get(pk=1)
            date = setting.upload_date.strftime('%Y-%m')
        except UploadSetting.DoesNotExist:
           return False
    
    
    if template > 2 or template < 0:
        return False
    
    file_name = '%s_%s.csv' % (date, reports[template])
    
    file_path = '%s/reports/%s' % (settings.MEDIA_ROOT, file_name)
    
    
    if not os.path.isfile(file_path):
        return False
    else:
        with open(file_path, 'U') as csv_file:   
            template_data = list(csv.reader(csv_file, dialect='excel-tab'))

    return template_data


@login_required(login_url='/admin/login')
def download_funds(request):
    template_data = { }
    user = request.user
    
    try:
        allowed = check_user_permissions(user, ['admin'])
    except:
        allowed = False
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment;filename="funds.csv"'
    writer = csv.writer(response)
    
    if allowed:
        funds = Fund.objects.all()
        writer.writerow(['Group Code', 'Fund Code', 'Fund Name',  'Fund Type', 'Fund Category', 'Investment Type', 'Fund Registration Date', 'Company Type', 'Index', 'Sales Fee', 'RRSP', 'Comments'])
        # writer.writerow(['Group Name', 'Group Code', 'Fund Name', 'Fund Code', 'Fund Type', 'Fund Category', 'Fund Registration Date', 'Company Type', 'Classification', 'Sales Fee', 'Index', 'RRSP', 'Active', 'Investment Type', 'Comments'])
        for fund in funds:
            sales_fee = Fund.NONE
            for s in Fund.SALES_FEE_CHOICES:
                if s[0] == fund.sales_fee:
                    sales_fee = s[1]
                    break
            if fund.index:
                index = 'Yes'
            else:
                index = 'No'
                
            if fund.rrsp:
                rrsp = 'Yes'
            else:
                rrsp = 'No'
            
            writer.writerow(['%s' % fund.contributer.code.upper().encode('utf8'), '%s' % fund.code.upper(), fund.name.encode('utf8'),'%s' % fund.type.name , '%s' % fund.category.name.encode('utf8'), fund.investment_type.name, '%s' % fund.registration_date, '%s' % fund.company_type.name, index, sales_fee, rrsp, '%s' % fund.comments])  
            # writer.writerow(['%s' % fund.contributer.name.encode('utf8'), '%s' % fund.contributer.code.upper().encode('utf8'), '%s' % fund.name.encode('utf8'), '%s' % fund.code.upper(), '%s' % fund.type.name , '%s' % fund.category.name.encode('utf8'), '%s' % fund.registration_date, '%s' % fund.company_type.name, '%s' % fund.classification.name, sales_fee, index, rrsp, active, fund.investment_type.name, '%s' % fund.comments])
        
    return response
    

@login_required(login_url='/admin/login')
def open_template_grid(request, id=None, template=None, month=None, year=None):
    
    template_data = { }
    errors = []
    user = request.user
    template_data['user'] = user
    template_data['id'] = id
    template_data['template'] = template
    template_data['month'] = month
    template_data['year'] = year
    
    try:
        date = datetime.datetime(int(year), int(month), 1)
    except UploadSetting.DoesNotExist:
        date = datetime.datetime.now().strftime('%Y-%m')
    
    
    if template != None:
        if template > 2 or template < 0:
            errors.append('Invalid template index.')
    else:
        errors.append('No template index.')
    
    file_name = '%s-%s_template%s.csv' % (year, month, template)
    try:
        contributer = Contributer.objects.get(pk=id)
        file_path = '%s/uploads/%s/%s' % (settings.MEDIA_ROOT, contributer.id, file_name)
        
        if not os.path.isfile(file_path):
            errors.append('File does not exist')
        else:
            import re       
            with open(file_path, 'U') as csv_file:
                csv_data = list(csv.reader(csv_file, dialect='excel-tab'))
                
                clean_data =[]
                for data in csv_data:
                    
                    new_column_data = []
                    column_count = 0
                    for column in data:
                        new_data = column.encode('utf-8')
                        new_data = new_data.replace('/t', '')
                        if column_count == 1:                        
                            pass
                            
                        column_count = column_count + 1
                        
                        new_column_data.append(new_data)
                        
                    clean_data.append(new_column_data)
                
                    
                template_data['data'] = simplejson.dumps(clean_data)
                
        template_data['errors'] = errors
        valid_template = ValidTemplate.objects.get(contributer=contributer, date__year=year, date__month=month)
        template_data['template_errors'] = TemplateError.objects.filter(valid_template=valid_template.id, template=template)
        
    except Contributer.DoesNotExist:
        errors.append('Group doesn\'t exist')
    except ValidTemplate.DoesNotExist:
        errors.append('Template does not exist')
   
    if len(errors) > 0:
        template_data['errors'] = errors
                    
    return render_to_response('grid.html', template_data)

@login_required(login_url='/admin/login')
def download_template(request, id=None, template = None, month=None, year=None):
    user = request.user
    errors = []
    
    try:
        allowed = check_user_permissions(user, ['admin'])
    except:
        allowed = False
        
    if allowed:
        if template != None:                
            if int(template) > 2 and int(template) < 0:
                errors.append('Invalid template index.')

            if year == None:
                errors.append('Invalid Year')
                
            if month == None:
                errors.append('Invalid month')
                
            if len(errors) == 0:
                file_name = '%s-%s_template%s.csv' % (year, month, template)
       
                try:
                    contributer = Contributer.objects.get(pk=id)
                    file_path = '%s/uploads/%s/%s' % (settings.MEDIA_ROOT, contributer.id, file_name)
                    
                    if os.path.isfile(file_path):
                        file = open(file_path,"r")
                        mimetype = mimetypes.guess_type(file_path)[0]
                        if not mimetype: mimetype = "application/octet-stream"
    
                        response = HttpResponse(file.read(), mimetype=mimetype)
                        response["Content-Disposition"]= "attachment; filename=%s" % os.path.split(file_name)[1]
                        return response
                    
                except Contributer.DoesNotExist:
                    pass
            
    
    return HttpResponse()
                         

@login_required(login_url='/admin/login')
def download_user_list(request):
    current_user = request.user
    errors = []
    try:
        allowed = check_user_permissions(current_user, ['admin'])
    except:
        allowed = False
    
    if allowed:
        response = HttpResponse(mimetype='application/x-download')
        response['Content-Disposition'] = 'attachment; filename=users.csv'
        
        writer = csv.writer(response)
        writer.writerow(['User ID', 'Username', 'Email', 'Type', 'First Name', 'Last Name', 'Phone', 'Company', 'Position', 'Department', 'Created',  'Active'])
        users = User.objects.all()
        for user in users:
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.phone:
                    phone = profile.phone
                    if profile.extension:
                        phone = '%s ext %s' % (phone, profile.extension)
                else:
                    phone = 'n/a'
                    
                if profile.company:
                    company = profile.company
                else:
                    company = 'n/a'    
                
                if profile.position:
                    position = profile.position
                else:
                    position = 'n/a'
                
                if profile.department:
                    department = profile.department
                else:
                    department = 'n/a' 
                
                if user.is_active:
                    active = 'Active'
                else:
                    active = 'Not Active'                 
                
                writer.writerow([user.id, user.username, user.email, profile.user_type.type, user.first_name, user.last_name, phone, company, position, department, user.date_joined,  active])
            except UserProfile.DoesNotExist:
                pass
            
    return response    

@login_required(login_url='/admin/login')  
def download_view(request, view):
    
    user = request.user
    errors = []
    try:
        allowed = check_user_permissions(user, ['admin'])
    except:
        allowed = False
    
    
    if allowed:
          
        try:
            setting = UploadSetting.objects.get(pk=1)
            date = setting.upload_date.strftime('%Y-%m')
        except UploadSetting.DoesNotExist:
            errors.append('Upload date not defined')
            
        if int(view) >= 0 and int(view) < 3: 
            views = ['stand_alone_view', 'primary_investment_management', 'funds_administration_view']
            view = int(view)
            
            file_path = '%s/reports/%s_%s.csv' % (settings.MEDIA_ROOT,  date, views[view])
            download_file = '%s_%s.csv' % (date, views[view])
            
            if os.path.isfile(file_path):
                report_data = open(file_path, "rb").read()
                response =  HttpResponse(report_data, mimetype='text/csv')
                response['Content-Disposition'] = 'attachment; filename=%s' % download_file
                return response
            else:
                pass
                
        else:
            errors.append('Invalid view')
            
def download_public(request, filename):
    
    try:
        file_path = '%s/samples/%s' % (settings.MEDIA_ROOT, filename)
        file = open(file_path,"r")
        mimetype = mimetypes.guess_type(filename)[0]
        if not mimetype: mimetype = "application/octet-stream"
    
        response = HttpResponse(file.read(), mimetype=mimetype)
        response["Content-Disposition"]= "attachment; filename=%s" % os.path.split(filename)[1]
        return response
    except Exception as e:
        return render_to_response('home_info.html')

