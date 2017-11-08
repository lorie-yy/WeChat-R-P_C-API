# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TwechatOffline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('usermac', models.CharField(max_length=32)),
                ('openid', models.CharField(max_length=32)),
                ('orderid', models.CharField(max_length=32)),
                ('type', models.CharField(default=b'0', max_length=4)),
                ('subscribe', models.CharField(default=b'0', max_length=1)),
                ('shopid', models.IntegerField()),
                ('cloudid', models.CharField(max_length=32, null=True, blank=True)),
            ],
        ),
    ]
