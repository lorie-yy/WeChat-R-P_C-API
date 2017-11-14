from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    '',
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
)
