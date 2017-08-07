# -*- coding:utf-8 -*-
from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    '',
    # url(r'^', shop_views.IndexView.as_view(), name='index'),
    url(r'^$',views.IndexView.as_view(), name='index'),
    url(r'^index',views.IndexView.as_view(), name='index'),
    url(r'^add_license',views.AddLicenseView.as_view(), name='add_license'),
    url(r'^add_cloud',views.AddCloudView.as_view(), name='add_cloud'),
    url(r'^lisence_login',views.lisence_login, name='lisence_login'),
    url(r'^license_register',views.license_register, name='license_register'),
    url(r'^license_activate',views.ActivateLicenseView.as_view(), name='license_activate'),
    url(r'^license_invalid',views.ValidateLicenseView.as_view(), name='license_invalid'),
)