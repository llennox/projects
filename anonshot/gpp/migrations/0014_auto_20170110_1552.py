# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-10 15:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gpp', '0013_photo_caption'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comments',
            name='postedByuuid',
        ),
        migrations.AddField(
            model_name='comments',
            name='postedBy',
            field=models.CharField(default='anon', max_length=255),
        ),
    ]
