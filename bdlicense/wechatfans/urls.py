from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    '',
    url(r'^getauthdata',views.TAuthdata.as_view(), name='getauthdata'),
    url(r'^getfansnumber',views.Getfansnumber.as_view(), name='getfansnumber'),
    url(r'^sub_detail',views.Sub_detail.as_view(), name='sub_detail'),
    url(r'^showfans',views.showfans, name='showfans'),
)
