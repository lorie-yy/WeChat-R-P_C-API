# -*- coding:utf-8 -*-
from django.db import models

# Create your models here.
class LicenseType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=100, null=False, blank=False)
    discription = models.CharField(max_length=255, default="")

class CloudInfo(models.Model):
    id = models.AutoField(primary_key=True)
    maxAPs = models.IntegerField('最大AP数',default=0, blank=False,)
    maxACs = models.IntegerField('最大AC数',default=0, blank=False)
    maxUsers = models.IntegerField('最大用户数',default=0, blank=False)

class LicenseRecord(models.Model):

    CLOSE = 0
    OPEN = 1
    LicenseStatusChoices = ((CLOSE, '未激活'),
                          (OPEN, '已激活'))

    id = models.AutoField(primary_key=True)
    key_id = models.CharField(max_length=255, null=False, blank=False)
    discription = models.CharField('云平台信息描述',max_length=255, default="")
    license_code = models.CharField(max_length=255, null=False, blank=False)
    license_status = models.IntegerField(choices=LicenseStatusChoices,verbose_name='license状态')#0:close;1:open
    licensetype= models.ForeignKey(LicenseType)
    cloudInfo = models.ForeignKey(CloudInfo)
    build_time = models.DateTimeField(auto_now_add=True)
    expire_time = models.DateTimeField('过期时间', blank=True, null=True)

