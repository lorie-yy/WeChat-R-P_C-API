# -*- coding:utf-8 -*-
from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    '',
    # url(r'^', shop_views.IndexView.as_view(), name='index'),
    url(r'^$',views.IndexView.as_view(), name='index'),
    url(r'^index',views.IndexView.as_view(), name='index'),
    url(r'^license_yun',views.IndexViewYun.as_view(), name='license_yun'),
    url(r'^user_list',views.UserIndexView.as_view(), name='user_list'),
    url(r'^add_license',views.AddLicenseView.as_view(), name='add_license'),
    url(r'^add_cloud',views.AddCloudView.as_view(), name='add_cloud'),
    url(r'^add_user',views.AddUserView.as_view(), name='add_user'),
    url(r'^user_cloud',views.UserCloudView.as_view(), name='user_cloud'),
    url(r'^modify_password',views.ModifyPasswordView.as_view(), name='modify_password'),
    url(r'^license_login',views.license_login, name='license_login'),
    url(r'^license_logout',views.license_logout, name='license_logout'),
    url(r'^license_activate',views.ActivateLicenseView.as_view(), name='license_activate'),
    url(r'^license_invalid',views.ValidateLicenseView.as_view(), name='license_invalid'),
    url(r'^user_invalid',views.ValidateUserView.as_view(), name='user_invalid'),
)