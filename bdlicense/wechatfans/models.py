from django.db import models


class TwechatOffline(models.Model):
    usermac = models.CharField(max_length=32)
    openid = models.CharField(max_length=32)
    orderid = models.CharField(max_length=32)
    type = models.CharField(max_length=4,default='0')
    subscribe = models.CharField(max_length=1,default='0')
    shopid = models.IntegerField()
    cloudid = models.CharField(max_length=32,null=True,blank=True)
