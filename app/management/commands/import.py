from django.core.management import BaseCommand, CommandError
from django.template.loader import render_to_string
from datetime import date, timedelta, datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from app.models import CompanyType, Contributer, Fund, FundCategory, FundClassification, FundType, Industry, InvestmentType, UserProfile, UserType

import calendar
import os
import csv

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        try:
            
            if args[0] == 'groups':
                print 'Importing Groups' 
                file_path = args[1]
                
                if not os.path.isfile(file_path):
                    print 'Cannot find file'
                else:
                    with open(file_path, 'U') as csv_file:   
                        template_data = list(csv.reader(csv_file, delimiter=','))
                        
                    index = 0
                    for data in template_data:
                        if index > 0:
                            try:
                                
                                try:
                                    Contributer.objects.get(code=data[0].lower())
                                    print 'Group already exists'
                                    pass
                                except Contributer.DoesNotExist:
                                    if len(data[0]) > 0:
                                        industry = Industry.objects.get(code=data[1])
                                        print 'Found Industry Type'
                                        
                                        group = Contributer()
                                        group.code = data[0].lower()
                                        group.name = data[2]
                                        group.industry = industry
                                            
                                        group.save()
                                        
                                        print 'Group Created'
                                        
                            except Industry.DoesNotExist:
                                print 'Group type does not exist %s'  % data[1]
    
                                
                        index = index + 1
             
            if args[0] == 'funds':
                          
                print 'Import Funds'
                file_path = args[1]
        
                if not os.path.isfile(file_path):
                    print 'Cannot find file'
                else:
                    with open(file_path, 'U') as csv_file:   
                        template_data = list(csv.reader(csv_file, delimiter=','))
                    
                    index = 0
                    for data in template_data:
                        if index > 0:
                            
                            try:
                                group = Contributer.objects.get(code=data[1].lower())
                                Fund.objects.get(code=data[2].lower(), contributer=group)
                                print 'Fund Already Exists'
                            except Contributer.DoesNotExist:
                                print 'Group does not exist %s' % data[1]
                            except Fund.DoesNotExist:
                                try:
                                    investment_type = InvestmentType.objects.get(name=data[5])
                                    print 'Found Investment Type'
                                    
                                    if len(data[10]) > 0:
                                        company_type = CompanyType.objects.get(name=data[10])
                                        print 'Found Company Type'
                                    else:
                                        company_type = CompanyType.objects.get(name='Trust')
                                    
                                    fund_type = FundType.objects.get(name=data[3])
                                    print 'Found Fund Type'
                                    
                                    fund_category = FundCategory.objects.get(name=data[4])
                                    print 'Found Fund Category'
                                    
                                    #fund_classification = FundClassification.objects.get(name=)
                                    print 'Sales Fee: %s' % data[7]
                                    
                                    fund = Fund()
                                    fund.code = data[2].lower()
                                    fund.contributer = group
                                    fund.type = fund_type
                                    fund.category = fund_category
                                    fund.investment_type = investment_type
                                    fund.name = data[9]
                                    fund.company_type = company_type
                                    fund.classification = FundClassification.objects.get(name='Mutual Fund')
                                    
                                    if(data[11] == 'N'):
                                        fund.index = False
                                    else:
                                        fund.index = True
                                        
                                    fund.active = True
                                    
                                    if(data[6] == 'Y'):
                                        fund.rrsp = True
                                    else:
                                        fund.rrsp = False
                                    
                                    fund.save()
                                    print 'Fund Saved'
                                    
                                except InvestmentType.DoesNotExist:
                                    print 'Could not find investment type %s' % data[5]
                                except CompanyType.DoesNotExist:
                                    print 'Could not find company type %s' % data[10]
                                except FundType.DoesNotExist:
                                    print 'Could not find fund type %s' % data[3]
                                except FundCategory.DoesNotExist:
                                    print 'Could not find fund category %s' % data[4]
                                except Exception as e:
                                    print 'Could not save fund %s' % data[2]
                                    print e                                             
                        
                        index = index + 1
            
            if args[0] == 'relationships':
                
                print 'Creating Fund Relationships'
                file_path = args[1]
        
                if not os.path.isfile(file_path):
                    print 'Cannot find file'
                else:
                    with open(file_path, 'U') as csv_file:   
                        template_data = list(csv.reader(csv_file, delimiter=','))
                        
                
                index = 0
                for data in template_data:
                    if index > 0:
                        try:
                            fof_code = data[1].lower().split('*')
                            
                            if len(fof_code) == 2:
                                group = Contributer.objects.get(code=fof_code[0])
                                fund = Fund.objects.get(contributer=group, code=fof_code[1])
                                
                                standalone_code = data[4].lower().split('*')
                                
                                if len(standalone_code) == 2:
                                    try:
                                        standalone_group = Contributer.objects.get(code=standalone_code[0])
                                        standalone_fund = Fund.objects.get(contributer=standalone_group, code=standalone_code[1])
                                        
                                        if standalone_fund not in fund.funds.all():
                                            print 'Creating Relationship'
                                            fund.funds.add(standalone_fund)
                                            
                                    except Contributer.DoesNotExist:
                                        print 'Stand Alone group %s does not exist' % standalone_code[0]
                                    except Fund.DoesNotExist:
                                        print 'Stand Alone fund %s Does not exist' % standalone_code[1]
                                        
                                else:
                                    print 'Invalid stand alone code %s' % data[4].lower()
                                    
                            else:
                                print 'Invalid fof code %s' % data[1].lower()
                            
                        except Contributer.DoesNotExist:
                            print 'Group %s does not exist ific code %s' % (fof_code[0], data[1].lower())
                        except Fund.DoesNotExist:
                            print 'Fund %s does not exist ific code %s' % (fof_code[1], data[1].lower())
                    
                    index = index + 1
            
            if args[0] == 'users':
                print 'Creating Users'
                file_path = args[1]
                
                if not os.path.isfile(file_path):
                    print 'Cannot find file'
                else:
                    with open(file_path, 'U') as csv_file:   
                        template_data = list(csv.reader(csv_file, delimiter=','))
            
                index = 0
                for data in template_data:
                    if index > 1:
                        try:
                            if len(User.objects.filter(username=data[11].strip())) == 0:
                                user_type = data[1].strip()
                                is_purse = False
                                if user_type == 'Contributor': 
                                    if data[10].strip() == 'PURSE':
                                        print 'Creating contributor: %s' % data[11]
                                        new_user = User.objects.create_user(data[11].strip(), data[8].strip(), data[12].strip())
                                        new_user.first_name = data[4].strip()
                                        new_user.last_name = data[5].strip()
                                        
                                        new_user.save()
                                        new_profile = UserProfile()
                                        new_profile.user = new_user
                                        new_profile.user_type = UserType.objects.get(type='contributer')
                                        new_profile.derpartment = data[6].strip()
                                        new_profile.position = data[7].strip()
                                        new_profile.company = data[0].strip()
                                        
                                        if len(data[9]) > 0:
                                            phone_parts = data[9].strip().split('x.')
                                            new_profile.phone = phone_parts[0]
                                            if len(phone_parts) == 2:
                                                new_profile.extension = phone_parts[1]
                                            
                                        if data[2].strip() == 'Member':
                                            new_profile.member = True
                                        else:
                                            new_profile.member = False
                                        
                                        new_profile.save()
                                        group_code = data[3].strip().lower()
                                        group = Contributer.objects.get(code=group_code)
                                        
                                        if new_user not in group.users.all():
                                            group.users.add(new_user)
                                            
                                        group.save()
                                        
                                if user_type == 'Subscriber':
                                    print 'Creating subscriber: %s' % data[11]
                                    new_user = User.objects.create_user(data[11].strip(), data[8].strip(), data[12].strip())
                                    new_user.first_name = data[4].strip()
                                    new_user.last_name = data[5].strip()
                                    
                                    new_user.save()
                                    new_profile = UserProfile()
                                    new_profile.user = new_user
                                    new_profile.user_type = UserType.objects.get(type='subscriber')
                                    new_profile.derpartment = data[6].strip()
                                    new_profile.position = data[7].strip()
                                    new_profile.company = data[0].strip()
                                    
                                    if len(data[9]) > 0:
                                        phone_parts = data[9].strip().split('x.')
                                        new_profile.phone = phone_parts[0]
                                        if len(phone_parts) == 2:
                                            new_profile.extension = phone_parts[1]
                                        
                                    if data[2].strip() == 'Member':
                                        new_profile.member = True
                                    else:
                                        new_profile.member = False
                                        
                                    new_profile.save()         
                            else:
                                print 'Username %s exist in system already' % data[11]
                                      
                        except Contributer.DoesNotExist:
                            print 'Group %s does not exist' % group_code
                        except Exception as e:
                            print e
                            print 'Could not create user %s' % data[11]
                    
                    
                    index = index + 1
                    
            
        except Exception as e:
            print e
            pass
            
            
        
        