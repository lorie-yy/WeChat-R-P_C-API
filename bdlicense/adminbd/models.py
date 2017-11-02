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
    code = models.CharField('物料编码',max_length=255,default='', blank=False)
    cloudRankName = models.CharField('物料名称',max_length=255,default='', blank=False)
    maxAPs = models.IntegerField('最大AP数',default=0, blank=False)
    maxACs = models.IntegerField('最大AC数',default=0, blank=False)
    maxUsers = models.IntegerField('最大用户数',default=0, blank=False)
    vesion_type = models.IntegerField('版本类型',default=1, blank=False)
    product_type = models.IntegerField('版本类型',default=1, blank=False)

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
    license_code = models.CharField(max_length=255, null=False, blank=False,unique=True)
    license_status = models.IntegerField(choices=LicenseStatusChoices,verbose_name='license状态',default=0)#0:close;1:open
    # low_counts = models.IntegerField(null=True,default=0)
    # mid_counts = models.IntegerField(null=True,default=0)
    # high_counts = models.IntegerField(null=True,default=0)
    maxAps = models.IntegerField(null=True,default=0)
    maxAcs = models.IntegerField(null=True,default=0)
    maxUsers = models.IntegerField(null=True,default=0)
    is_valid = models.IntegerField(null=True,default=1)#0:无效；1:有效,2:已注册
    is_reset = models.IntegerField(null=True,default=1)#0:重置的license；1:未重置过
    random_num = models.CharField(max_length=16,null=True,default='')#license对应的随机数
    # licenseType= models.ForeignKey(LicenseType)
    licenseType= models.CharField(max_length=255, null=True, blank=False,default='1')
    licenseParam = models.ManyToManyField(LicenseParams,default=None, null=True)
    cloudInfo = models.ForeignKey(CloudInformation)
    build_time = models.DateTimeField(auto_now_add=True)
    expire_time = models.DateTimeField('过期时间', blank=True, null=True)


class WorkOrderNum(models.Model):
    id = models.AutoField(primary_key=True)
    workOrderNum = models.CharField(max_length=255, null=True, blank=False,default='')
    license = models.ForeignKey(LicenseRecord)

class WorkOrderInformation(models.Model):
    id = models.AutoField(primary_key=True)
    materiel_name = models.CharField(max_length=255, null=True, blank=False,default='')
    materiel_count = models.CharField(max_length=255, null=True, blank=False,default='')
    workordernum = models.ForeignKey(WorkOrderNum)
    # params = models.ForeignKey(LicenseParams)


class SystemConfig(models.Model):
    id = models.AutoField(primary_key=True)
    attribute = models.CharField(max_length=64, db_index=True, unique=True)
    value = models.CharField(max_length=253)
    description = models.CharField(max_length=253, blank=True, null = True)

    class Meta:
        managed = True
        db_table = 'system_config'

    def __unicode__(self):
        return u'%s = %s, %s ' % (self.attribute, self.value, self.description)

    @staticmethod
    def getAttrValue(_attr):
        records = SystemConfig.objects.filter(attribute=_attr)
        if records.count() == 1:
            return records[0].value, True
        else:
            # error: miss the configuration
            print ("attribute %s doesn't exist in system_config table \n" % (_attr))
            return '', False