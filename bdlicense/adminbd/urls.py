# -*- coding:utf-8 -*-
from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    '',
    # url(r'^', shop_views.IndexView.as_view(), name='index'),
    url(r'^$',views.IndexView.as_view(), name='index'),
    url(r'^index',views.IndexView.as_view(), name='index'),
    url(r'^license_yun',views.IndexViewYun.as_view(), name='license_yun'),
    url(r'^del_cloud',views.delCloudView.as_view(), name='del_cloud'),
    url(r'^user_list',views.UserIndexView.as_view(), name='user_list'),
    url(r'^add_license',views.AddLicenseView.as_view(), name='add_license'),
    url(r'^edit_license',views.EditLicenseView.as_view(), name='edit_license'),
    url(r'^add_cloud',views.AddCloudView.as_view(), name='add_cloud'),
    url(r'^add_user',views.AddUserView.as_view(), name='add_user'),
    url(r'^user_cloud',views.UserCloudView.as_view(), name='user_cloud'),
    url(r'^license_param',views.KeyParamsView.as_view(), name='license_param'),
    url(r'^modify_password',views.ModifyPasswordView.as_view(), name='modify_password'),
    url(r'^license_login',views.license_login, name='license_login'),
    url(r'^license_logout',views.license_logout, name='license_logout'),
    url(r'^license_activate',views.ActivateLicenseView.as_view(), name='license_activate'),
    url(r'^update_key_id',views.UpdateKeyIDView.as_view(), name='update_key_id'),
    url(r'^license_register',views.RegisterLicenseView.as_view(), name='license_register'),
    url(r'^trial_license_register',views.TrialRegisterLicenseView.as_view(), name='trial_license_register'),
    url(r'^register_result',views.RegisterResultView.as_view(), name='register_result'),
    url(r'^license_invalid',views.ValidateLicenseView.as_view(), name='license_invalid'),
    url(r'^user_invalid',views.ValidateUserView.as_view(), name='user_invalid'),
    url(r'^reset_license',views.LicenseResetView.as_view(), name='reset_license'),
    url(r'^license_reset_result',views.LicenseResetResultView.as_view(), name='license_reset_result'),
    # url(r'^download_license_client_file',views.download_license_file, name='download_license_client_file'),
    # url(r'^download_license_usage_file',views.download_hlep_usage_file, name='download_license_usage_file'),
    url(r'^download_file',views.download_file, name='download_file'),
    url(r'^work_order',views.get_work_order_info, name='work_order'),
    url(r'^sys_config',views.SysConfigView.as_view(), name='sys_config'),
    url(r'^or_query',views.or_query.as_view(), name='or_query'),
    url(r'^order_details',views.order_details.as_view(), name='order_details'),
    url(r'^tmp_cloud',views.TmpCloud.as_view(), name='tmp_cloud'),
)