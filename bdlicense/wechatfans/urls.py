from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    '',
    url(r'^register',views.Register.as_view(), name='register'),
    url(r'^getauthdata',views.TAuthdata.as_view(), name='getauthdata'),
    url(r'^getfansnumber',views.Getfansnumber.as_view(), name='getfansnumber'),
    url(r'^sub_detail',views.Sub_detail.as_view(), name='sub_detail'),
    url(r'^getthirdpartinfo',views.getThirdpartInfo, name='getthirdpartinfo'),
    url(r'^savethirdpartinfo',views.saveThirdpartInfo, name='savethirdpartinfo'),
    url(r'^getcloudname',views.getCloudname, name='getCloudname'),
    url(r'^savecloudconfig',views.saveCloudconfig, name='savecloudconfig'),
    url(r'^getcloudconfig',views.getCloudConfig, name='getcloudconfig'),
)
