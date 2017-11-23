from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    '',
    url(r'^register',views.Register.as_view(), name='register'),
    url(r'^logout',views.logout, name='logout'),
    url(r'^modify_password',views.modify_password, name='modify_password'),
    url(r'^getauthdata',views.TAuthdata.as_view(), name='getauthdata'),
    url(r'^getfansnumber',views.Getfansnumber.as_view(), name='getfansnumber'),
    url(r'^sub_detail',views.Sub_detail.as_view(), name='sub_detail'),
    url(r'^showfans',views.showfans, name='showfans'),
    url(r'^takemoney',views.takemoney, name='takemoney'),
    url(r'^getthirdpartinfo',views.getThirdpartInfo, name='getthirdpartinfo'),
    url(r'^savethirdpartinfo',views.saveThirdpartInfo, name='savethirdpartinfo'),
    url(r'^getcloudname',views.getCloudname, name='getCloudname'),
    url(r'^savecloudconfig',views.saveCloudconfig, name='savecloudconfig'),
    url(r'^getcloudconfig',views.getCloudConfig, name='getcloudconfig'),
    url(r'^apply_for_withdrawal',views.apply_for_withdrawal, name='apply_for_withdrawal'),
    url(r'^getshopid',views.getshopid, name='getshopid'),
    url(r'^savediscountinfo',views.savediscountinfo, name='savediscountinfo'),
    url(r'^getalldiscountinfo',views.getalldiscountinfo, name='getalldiscountinfo'),
    url(r'^getapplyforwithdrawal',views.getApplyforWithdrawal, name='getapplyforwithdrawal'),
    url(r'^getallapplyforwithdrawalrecords',views.getallApplyforWithdrawalRecords, name='getallapplyforwithdrawalrecords'),
    url(r'^transferaccounts',views.Transferaccounts.as_view(), name='transferaccounts'),
    url(r'^applyfor_records',views.applyfor_records, name='applyfor_records'),
    url(r'closerecord',views.closerecord, name='closerecord'),
    url(r'^getallprofit',views.getAllProfit, name='getallprofit'),
)
