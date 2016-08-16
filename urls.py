from django.conf.urls.defaults import patterns, include, url

import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ific.views.home', name='home'),
    # url(r'^ific/', include('ific.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^backend/', include(admin.site.urls)),
    
    # Contributer URLS
    url(r'^admin/group/add$', 'app.views.views.add_contributer'),
    url(r'^admin/group/edit/(?P<id>\d+)', 'app.views.views.edit_contributer'),
    url(r'^admin/groups', 'app.views.views.contributers'),
    
    url(r'^admin/user/add', 'app.views.views.add_user'),
    url(r'^admin/user/edit/(?P<id>\d+)', 'app.views.views.edit_user'),
    
    #Users
    url(r'^admin/users', 'app.views.views.users'),
    
    # Login/Logout URLs
    url(r'^admin/login$', 'app.views.views.login'),
    url(r'^admin/logout', 'app.views.views.logout'),
    
    # List Management URLS
    url(r'^admin/lists/(?P<type>\w+)$', 'app.views.views.list_management'),
    url(r'^admin/lists$', 'app.views.views.list_management'),
    
    # Upload Data
    url(r'^admin/upload$', 'app.views.views.upload'),
    url(r'^admin/upload/file$', 'app.views.views.upload_file'),
    url(r'^admin/upload/timeseries$', 'app.views.views.upload_timeseries'),
    
    # Fund URLS
    url(r'^admin/fund/add', 'app.views.views.add_fund'),
    url(r'^admin/fund/delete/(?P<id>\d+)', 'app.views.views.delete_fund'),
    url(r'^admin/fund/edit/(?P<id>\d+)', 'app.views.views.edit_fund'),

    url(r'^admin/funds/(?P<offset>\d+)/(?P<order>\w+)/(?P<asc>\w+)', 'app.views.views.funds'),
    url(r'^admin/funds', 'app.views.views.funds'),
    url(r'^admin/validation', 'app.views.views.validation'),
    
    
    url(r'^admin/download/(?P<id>\d+)/(?P<year>\d{4})/(?P<month>\d{2})/$', 'app.views.views.download'),
    url(r'^admin/download/template/(?P<id>\d+)/(?P<template>\d+)/(?P<month>\d{2})/(?P<year>\d{4})/$', 'app.views.views.download_template'),
    url(r'^admin/download/view/(?P<view>\d+)$', 'app.views.views.download_view'),
    url(r'^admin/download/funds', 'app.views.views.download_funds'),
    url(r'^admin/download/users', 'app.views.views.download_user_list'),
    url(r'^admin/logs', 'app.views.views.logs'),
    url(r'^admin/packages', 'app.views.views.packages'),
    url(r'^admin/package/add', 'app.views.views.add_package'),
    url(r'^admin/package/edit/(?P<id>\d+)', 'app.views.views.edit_package'),
    url(r'^admin/reports', 'app.views.views.reports'),
    url(r'^admin/statistics$', 'app.views.views.stats'),
    url(r'^admin/statistics/(?P<year>\d{4})/(?P<month>\d{2})/$', 'app.views.views.stats'),
    url(r'^admin/purchase$', 'app.views.views.purchase'),
    url(r'^admin/purchase/summary', 'app.views.views.purchase_summary'),
    url(r'^admin/transactions$', 'app.views.views.transactions'),
    url(r'^admin/transaction/add$', 'app.views.views.add_transaction'),
    url(r'^admin/transaction/edit/(?P<id>\d+)', 'app.views.views.edit_transaction'),
   
    url(r'^admin/utilities', 'app.views.views.utilities'),
    url(r'^admin/upload/settings', 'app.views.views.upload_settings'),
    url(r'^admin/open/template/(?P<id>\d+)/(?P<template>\d+)/(?P<year>\d+)/(?P<month>\d+)', 'app.views.views.open_template_grid'),

    
    # Consumer URLs
    url(r'^consumer/signup', 'app.views.views.consumer_signup'),
    url(r'^consumer/profile', 'app.views.views.edit_user'),
    
    # Public URLs
    url(r'^$', 'app.views.views.home'),
    url(r'^privacy', 'app.views.views.privacy'),
    #url(r'^terms', 'app.views.views.terms'),
    url(r'^info', 'app.views.views.home_info'),
    url(r'^download/(?P<filename>.*\w+)', 'app.views.views.download_public'),
    
    # Ajax URLS
    url(r'^admin/ajax/upload/settings$', 'app.views.ajax.views.ajax_upload_settings'),
    url(r'^admin/ajax/add/group$', 'app.views.ajax.views.ajax_add_contributer'),
    url(r'^admin/ajax/aggregate$', 'app.views.ajax.views.ajax_aggregate'),
    url(r'^admin/ajax/check/group/code$', 'app.views.ajax.views.ajax_check_contributer_code'),
    url(r'^admin/ajax/check/fund/code$', 'app.views.ajax.views.ajax_check_fund_code'),
    url(r'^admin/ajax/delete/group$', 'app.views.ajax.views.ajax_delete_contributer'),
    url(r'^admin/ajax/edit/group$', 'app.views.ajax.views.ajax_edit_contributer'),
    url(r'^admin/ajax/find/group$', 'app.views.ajax.views.ajax_find_contributer'),
    url(r'^admin/ajax/find/fund$', 'app.views.ajax.views.ajax_find_fund'),
    url(r'^admin/ajax/find/user$', 'app.views.ajax.views.ajax_find_user'),
    url(r'^admin/ajax/login/$', 'app.views.ajax.views.ajax_login'),
    url(r'^admin/ajax/purchase$', 'app.views.ajax.views.ajax_purchase'),
    url(r'^admin/ajax/upload/step$', 'app.views.ajax.views.ajax_upload_next'),
    url(r'^admin/ajax/validate$', 'app.views.ajax.views.ajax_validate'),
    url(r'^admin/ajax/complete$', 'app.views.ajax.views.ajax_complete'),
    url(r'^admin/ajax/upload/settings$', 'ajax_upload_settings'),
    url(r'^admin/ajax/save/report/(?P<id>\d+)/(?P<template>\d+)', 'app.views.ajax.views.ajax_save_report'),
    url(r'^admin/ajax/transaction/validate$', 'app.views.ajax.views.ajax_validate_transaction'),
    
    url(r'^admin/ajax/get/standalone$', 'app.views.ajax.views.get_standalone_result'),
    url(r'^admin/ajax/get/primary-investment$', 'app.views.ajax.views.get_primary_investment_result'),
    url(r'^admin/ajax/get/funds-admin$', 'app.views.ajax.views.get_funds_admin_result'),
    url(r'^admin/ajax/clear-result$', 'app.views.ajax.views.ajax_clear_result')
    
)

urlpatterns += patterns('',
    url(r'^files/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
)