# -*- coding:utf-8 -*-
from django.db import models


class TwechatOffline(models.Model):
    usermac = models.CharField('用户mac',max_length=32)
    apmac = models.CharField('AP mac',max_length=32,default='')
    openid = models.CharField(max_length=32)
    orderid = models.CharField('订单号',max_length=32)
    type = models.CharField('第三方flag',max_length=4,default='0')
    subscribe = models.CharField('关注与否',max_length=1,default='0')#0:未关注;1:已关注
    shopid = models.IntegerField('云平台商铺id',default=0)
    cloudid = models.CharField('云平台id',max_length=32,null=True,blank=True)
    authtime = models.DateTimeField('关注时间',auto_now_add=True)
    price = models.CharField('价格',max_length=4,default='0')
    settlement = models.CharField('是否结算',max_length=1,default='0')#0：不可以结算;1:可以结算;2:已结算
    gh_name = models.CharField('公众号名称',max_length=32,default='')
