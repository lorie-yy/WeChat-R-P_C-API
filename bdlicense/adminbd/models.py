# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Create your models here.
class ProfileBase(type):
    def __new__(cls,name,bases,attrs):
        module = attrs.pop('__module__')
        parents = [b for b in bases if isinstance(b, ProfileBase)]
        if parents:
            fields = []
            for obj_name, obj in attrs.items():
                if isinstance(obj, models.Field): fields.append(obj_name)
                User.add_to_class(obj_name, obj)
            UserAdmin.fieldsets = list(UserAdmin.fieldsets)
            UserAdmin.fieldsets.append((name, {'fields': fields}))
        return super(ProfileBase, cls).__new__(cls, name, bases, attrs)

class ProfileUser(object):
    __metaclass__ = ProfileBase

class AuthUser(ProfileUser):
    user_level = models.IntegerField('用户等级',default=0, blank=False)#0：销售用户 1：超级用户  2：工厂用户
    phone_num = models.CharField(max_length=254,default='')
    contacts = models.CharField(max_length=254,default='')
    class Meta:
        managed = True
        #db_table = 'auth_user'

    def __unicode__(self):
        return u'%s: %d ' % (self.username, self.id)

class LicenseType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=100, null=False, blank=False)#0基本
    discription = models.CharField(max_length=255, default="")

class LicenseParams(models.Model):
    id = models.AutoField(primary_key=True)
    cloudRankName = models.CharField('云平台等级名称',max_length=255,default='', blank=False)
    #1:lowLicense 2:middleLicense 3:highLicense
    maxAPs = models.IntegerField('最大AP数',default=0, blank=False)
    maxACs = models.IntegerField('最大AC数',default=0, blank=False)
    maxUsers = models.IntegerField('最大用户数',default=0, blank=False)

class CloudInformation(models.Model):
    id = models.AutoField(primary_key=True)
    cloudUser = models.ManyToManyField(User,null=True)
    cloudName = models.CharField('云平台名称',max_length=255,blank=False, default='')
    buyer = models.CharField('购买方',max_length=255,blank=True, null=True)
    buyTime = models.DateTimeField('购买时间',auto_now_add=True)
    installAddress = models.CharField('安装地址',max_length=255,blank=True, null=True)
    contacts = models.CharField('联系人',max_length=255,blank=True, null=True)
    phone = models.CharField('联系电话',max_length=255,blank=True, null=True)
    cloudNum = models.CharField('云平台编号',max_length=255,default='', blank=False)

    class Meta:
        verbose_name='云平台信息'
        verbose_name_plural='云平台信息'

class LicenseRecord(models.Model):

    CLOSE = 0
    OPEN = 1
    LicenseStatusChoices = ((CLOSE, '未激活'),
                          (OPEN, '已激活'))

    id = models.AutoField(primary_key=True)
    key_id = models.CharField(max_length=255, null=True, blank=False,default='')
    discription = models.CharField('云平台信息描述',max_length=255, default="")
    license_code = models.CharField(max_length=255, null=False, blank=False)
    license_status = models.IntegerField(choices=LicenseStatusChoices,verbose_name='license状态',default=0)#0:close;1:open
    counts = models.IntegerField(null=True,default=1)
    is_valid = models.IntegerField(null=True,default=1)#0:无效；1:有效,2:已注册
    is_reset = models.IntegerField(null=True,default=1)#0:重置的license；1:未重置过
    random_num = models.CharField(max_length=16,null=True,default='')#license对应的随机数
    licenseType= models.ForeignKey(LicenseType)
    licenseParam = models.ForeignKey(LicenseParams,default=None, null=True)
    cloudInfo = models.ForeignKey(CloudInformation)
    build_time = models.DateTimeField(auto_now_add=True)
    expire_time = models.DateTimeField('过期时间', blank=True, null=True)

