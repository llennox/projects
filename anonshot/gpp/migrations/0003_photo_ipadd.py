# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-20 21:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gpp', '0002_auto_20161220_2109'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='ipadd',
            field=models.CharField(default='anon', max_length=50),
        ),
    ]
