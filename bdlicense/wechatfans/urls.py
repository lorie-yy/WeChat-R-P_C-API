from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    '',
    url(r'^getauthdata',views.TAuthdata.as_view(), name='getauthdata'),
    url(r'^getfansnumber',views.Getfansnumber.as_view(), name='getfansnumber'),
)
