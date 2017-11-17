# -*- coding:utf-8 -*-
from django.db import models
from adminbd.models import CloudInformation


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

class ThridPartyConfig(models.Model):
    thirdpartname = models.CharField('第三方接口名称',max_length=16)
    url = models.CharField('url',max_length=256)
    type = models.CharField('类型',max_length=2,unique=True)

class CloudConfig(models.Model):
    cloudname = models.CharField('云平台名称',max_length=64,null=True,blank=True)
    cloudid = models.CharField('云平台编号',max_length=64)
    thirdpart = models.ForeignKey(ThridPartyConfig)

class ApplyforWithdrawalRecords(models.Model):
    ALIPAY = 1
    WIRE_TRANSFER = 2
    PaymentModeChoices = (
		(ALIPAY, '支付宝'),
		(WIRE_TRANSFER, '转账'),
		)
    paymentmode = models.IntegerField(choices=PaymentModeChoices, verbose_name='支付方式')
    cloudname = models.CharField('云平台名称',max_length=64)
    cloudid = models.CharField('云平台编号',max_length=64)
    shopid = models.IntegerField('云平台商铺id',default=0)
    username = models.CharField('用户名',max_length=32)
    applyfortime = models.DateTimeField('申请时间',auto_now_add=True)
    alipay_name=models.CharField('支付宝姓名',max_length=64)
    alipaynum=models.CharField('支付宝账号',max_length=64)
    company=models.CharField('公司名称',max_length=64)
    bank_name=models.CharField('开户行',max_length=64)
    banknum=models.CharField('银行卡账号',max_length=19)
    getmoney = models.IntegerField('提取金额(分)')
    RESULT_SUCCESS = 101
    RESULT_FAIL = 102
    RESULT_ACCESSPAY = 103
    PaymentResultChoices = (
		(RESULT_SUCCESS, '转账成功'),
		(RESULT_ACCESSPAY, '可转帐'),
		(RESULT_FAIL, '转账失败')
		)
    paymentresult = models.IntegerField(choices=PaymentResultChoices, verbose_name='支付结果')
    flag = models.IntegerField('标签',default=0)
    note = models.TextField(blank=True, verbose_name='备注')

class cloudtouser(models.Model):
    username = models.CharField('用户名',max_length=32)
    password = models.CharField('密码',max_length=32)
    cloudid = models.CharField('云平台编号',max_length=64)
    shopid = models.IntegerField('云平台商铺id')


class shop_discountinfo(models.Model):
    cloudid = models.CharField('云平台编号',max_length=64)
    shopid = models.IntegerField('云平台商铺id')
    discount = models.FloatField('云平台商铺折扣',default= 0.9)
    totalincome = models.IntegerField('总收益(分)',default= 0)      #打折
    availablecash = models.IntegerField('可提现(分)',default= 0)    #打折
    cashed = models.IntegerField('已提现(分)',default= 0)           #打折