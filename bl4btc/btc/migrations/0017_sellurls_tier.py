# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-19 18:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('btc', '0016_auto_20160917_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='sellurls',
            name='tier',
            field=models.IntegerField(default=0, max_length=1),
        ),
    ]
