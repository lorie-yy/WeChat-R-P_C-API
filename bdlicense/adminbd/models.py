# -*- coding:utf-8 -*-
from django.db import models

# Create your models here.
class LicenseType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=100, null=False, blank=False)
    discription = models.CharField(max_length=255, default="")

class LicenseRecord(models.Model):
    id = models.AutoField(primary_key=True)
    key_id = models.CharField(max_length=255, null=False, blank=False)
    license_code = models.CharField(max_length=255, null=False, blank=False)
    type= models.ForeignKey(LicenseType)
    record_time = models.DateTimeField(auto_now_add=True)