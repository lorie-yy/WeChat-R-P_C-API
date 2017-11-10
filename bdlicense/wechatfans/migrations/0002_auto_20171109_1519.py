# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('wechatfans', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='twechatoffline',
            name='apmac',
            field=models.CharField(default=b'', max_length=32, verbose_name=b'AP mac'),
        ),
        migrations.AddField(
            model_name='twechatoffline',
            name='authtime',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 9, 7, 19, 39, 383100, tzinfo=utc), verbose_name=b'\xe5\x85\xb3\xe6\xb3\xa8\xe6\x97\xb6\xe9\x97\xb4', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='twechatoffline',
            name='gh_name',
            field=models.CharField(default=b'', max_length=32, verbose_name=b'\xe5\x85\xac\xe4\xbc\x97\xe5\x8f\xb7\xe5\x90\x8d\xe7\xa7\xb0'),
        ),
        migrations.AddField(
            model_name='twechatoffline',
            name='price',
            field=models.CharField(default=b'0', max_length=4, verbose_name=b'\xe4\xbb\xb7\xe6\xa0\xbc'),
        ),
        migrations.AddField(
            model_name='twechatoffline',
            name='settlement',
            field=models.CharField(default=b'0', max_length=1, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe7\xbb\x93\xe7\xae\x97'),
        ),
        migrations.AlterField(
            model_name='twechatoffline',
            name='cloudid',
            field=models.CharField(max_length=32, null=True, verbose_name=b'\xe4\xba\x91\xe5\xb9\xb3\xe5\x8f\xb0id', blank=True),
        ),
        migrations.AlterField(
            model_name='twechatoffline',
            name='orderid',
            field=models.CharField(max_length=32, verbose_name=b'\xe8\xae\xa2\xe5\x8d\x95\xe5\x8f\xb7'),
        ),
        migrations.AlterField(
            model_name='twechatoffline',
            name='shopid',
            field=models.IntegerField(default=0, verbose_name=b'\xe4\xba\x91\xe5\xb9\xb3\xe5\x8f\xb0\xe5\x95\x86\xe9\x93\xbaid'),
        ),
        migrations.AlterField(
            model_name='twechatoffline',
            name='subscribe',
            field=models.CharField(default=b'0', max_length=1, verbose_name=b'\xe5\x85\xb3\xe6\xb3\xa8\xe4\xb8\x8e\xe5\x90\xa6'),
        ),
        migrations.AlterField(
            model_name='twechatoffline',
            name='type',
            field=models.CharField(default=b'0', max_length=4, verbose_name=b'\xe7\xac\xac\xe4\xb8\x89\xe6\x96\xb9flag'),
        ),
        migrations.AlterField(
            model_name='twechatoffline',
            name='usermac',
            field=models.CharField(max_length=32, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7mac'),
        ),
    ]
