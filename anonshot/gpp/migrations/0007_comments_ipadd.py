# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-28 20:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gpp', '0006_auto_20161222_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='ipadd',
            field=models.CharField(default='anon', max_length=50),
        ),
    ]
