from django.contrib.auth.models import User
from django.db import models

class Industry(models.Model):
    name = models.CharField(max_length=128, blank=True)
    code = models.CharField(max_length=2, unique=True)
    

class InvestmentType(models.Model):
    
    NONE = 0
    SELF = 1
    OTHER = 2
    ANY = 3
    
    COMPANY_CHOICES = (
                        (NONE, 'None'),
                        (SELF, 'Self'),
                        (OTHER, 'Other'),
                        (ANY, 'Any')
    )
    
    name = models.CharField(max_length=128)
    fund_of_fund = models.BooleanField(default=False)
    can_own = models.ForeignKey('self', null=True, default=None)  
    company = models.IntegerField(choices=COMPANY_CHOICES, default=0)

class CompanyType(models.Model):
    name = models.CharField(max_length=128, blank=True)

class Contributer(models.Model):
    name = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=3, unique=True)
    active = models.BooleanField(default=True)
    industry = models.ForeignKey(Industry)
    users = models.ManyToManyField(User)
    hide = models.BooleanField(default=False)
    
class FundCategory(models.Model):
    name = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=3, blank=True, unique=True)

class FundClassification(models.Model):
    name = models.CharField(max_length=255, blank=True)

class FundType(models.Model):
    name = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=2, blank=True, unique=True)

class Fund(models.Model):
    
    REDEMPTION = 'red'
    FRONT_END = 'fro'
    OPTIONAL = 'opt'
    NONE = 'non'
    
    SALES_FEE_CHOICES = ((REDEMPTION, 'Redemption'),
                         (FRONT_END, 'Front End'),
                         (OPTIONAL, 'Optional'),
                         (NONE, 'None')
    )
    
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=3)    
    registration_date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)
    index = models.BooleanField(default=True)
    rrsp = models.BooleanField(default=False)
    sales_fee = models.CharField(max_length=3, choices=SALES_FEE_CHOICES, blank=True)
    
    comments = models.CharField(max_length=255, blank=True)
    
    contributer = models.ForeignKey(Contributer)
    
    company_type = models.ForeignKey(CompanyType, default=None)
    category = models.ForeignKey(FundCategory, null=True, default=None)
    classification = models.ForeignKey(FundClassification, null=True, default=None)
    investment_type = models.ForeignKey(InvestmentType, null=True, default=None)
    
    type = models.ForeignKey(FundType)
        
    funds = models.ManyToManyField('self', symmetrical=False)
    
    class Meta:
        unique_together = (('contributer', 'code'))
    
class Reports(models.Model):
    name = models.CharField(max_length=128)
    file_type = models.CharField(max_length=4)
    quarterly = models.BooleanField(default=False)
    
class UserLog(models.Model):
    user = models.ForeignKey(User, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=16)

class UserType(models.Model):
    type = models.CharField(max_length=64)
    
class UserProfile(models.Model):
    
        
    user = models.OneToOneField(User)
    user_type = models.ForeignKey(UserType, blank=True)
    department = models.CharField(max_length=128, blank=True)
    company = models.CharField(max_length=128, blank=True)
    position = models.CharField(max_length=128, blank=True)
    phone = models.CharField(max_length=14, blank=True)
    extension = models.CharField(max_length=8, blank=True)
    member = models.BooleanField(default=False)
    
    suppressed = models.BooleanField(default=False, blank=True)
    reports = models.ManyToManyField(Reports)
    ip_address = models.CharField(max_length=16, blank=True, null=True)
    
       
class ValidTemplate(models.Model):
    contributer = models.ForeignKey(Contributer)
    
    template_one = models.BooleanField(default=False)
    template_two = models.BooleanField(default=False)
    template_three = models.BooleanField(default=False)
    
    date = models.DateField()

class TemplateError(models.Model):
    
    ERROR_TYPES = (
                   (0, 'Warning'),
                   (1, 'errors')    
    )
    
    valid_template = models.ForeignKey(ValidTemplate)
    error = models.CharField(max_length=255)
    template = models.IntegerField()
    error_type = models.IntegerField(choices=ERROR_TYPES, default=1)
    column = models.IntegerField(null=True, blank=True)
    row = models.IntegerField(null=True, blank=True)
    
class Package(models.Model):
    
    name = models.CharField(max_length=128)
    price = models.FloatField(null=True)
    per_file_price = models.FloatField(null=True)
    description = models.CharField(max_length=255)
    reports = models.ManyToManyField(Reports)
    monthly = models.BooleanField(default=False)
    quarterly = models.BooleanField(default=False)
    

class Transaction(models.Model):
    
    CREDIT_CARD = 'cc'
    CHEQUE = 'chq'
    
    TRANSACTION_TYPES = (
                         (CREDIT_CARD, 'Credit Card'),
                         (CHEQUE, 'Cheque')
    )
    
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User)
    package = models.ForeignKey(Package, null=True, blank=True)
    
    
    price = models.FloatField(default=0.00)
    expires = models.DateField(null=True, blank=True, default=None)
    type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, null=True, blank=True)
    receipt_number = models.CharField(max_length=30, blank=True, null=True)
    page_code = models.CharField(max_length=128, blank=True, null=True)
    
    valid = models.BooleanField(default=False)
    
class UploadSetting(models.Model):
    upload_date = models.DateField(null=True, blank=True)
    stop_upload_date = models.DateField(null=True, blank=True)  
    report_view_date = models.DateField(null=True, blank=True)  

class AllowedTemplate(models.Model):
     contributer = models.ForeignKey(Contributer)
     fund = models.ForeignKey(Fund)
     template_type = models.SmallIntegerField(default=2)
      

    