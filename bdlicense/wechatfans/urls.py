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
    url(r'^getthirdpartinfo',views.getThirdpartInfo.as_view(), name='getthirdpartinfo'),
    url(r'^savethirdpartinfo',views.saveThirdpartInfo, name='savethirdpartinfo'),
    url(r'^getcloudname',views.getCloudname, name='getCloudname'),
    url(r'^savecloudconfig',views.saveCloudconfig, name='savecloudconfig'),
    url(r'^getcloudconfig',views.getCloudConfig.as_view(), name='getcloudconfig'),
    url(r'^apply_for_withdrawal',views.apply_for_withdrawal, name='apply_for_withdrawal'),
    url(r'^getshopid',views.getshopid, name='getshopid'),
    url(r'^savediscountinfo',views.savediscountinfo, name='savediscountinfo'),
    url(r'^getalldiscountinfo',views.getalldiscountinfo.as_view(), name='getalldiscountinfo'),
    url(r'^getapplyforwithdrawal',views.getApplyforWithdrawal.as_view(), name='getapplyforwithdrawal'),
    url(r'^getallapplyforwithdrawalrecords',views.getallApplyforWithdrawalRecords.as_view(), name='getallapplyforwithdrawalrecords'),
    url(r'^transferaccounts',views.Transferaccounts.as_view(), name='transferaccounts'),
    url(r'^applyfor_records',views.applyfor_records, name='applyfor_records'),
    url(r'closerecord',views.closerecord, name='closerecord'),
    url(r'^getallprofit',views.getAllProfit.as_view(), name='getallprofit'),
    url(r'^getallfans',views.getAllFans.as_view(), name='getallfans'),
    url(r'^getrelation',views.getRelationBTWUserandCloud, name='getrelation'),
    url(r'^getcloudprofit',views.getCloudProfit.as_view(), name='getcloudprofit'),
    url(r'^getchildapply',views.getChildApply.as_view(), name='getchildapply'),
    url(r'^showallchildshopprofit',views.showAllChildshopProfit, name='showallchildshopprofit'),
    url(r'^addchild',views.addchild, name='addchild'),
    url(r'^edit_child_dis',views.edit_child_dis, name='edit_child_dis'),
    url(r'^showprofit',views.showProfit, name='showprofit'),
    url(r'^is_valid',views.is_valid, name='is_valid'),
    url(r'^update_everybodyprofit',views.update_everybodyprofit, name='update_everybodyprofit'),
    url(r'^update_userprice',views.update_userprice, name='update_userprice'),
)
