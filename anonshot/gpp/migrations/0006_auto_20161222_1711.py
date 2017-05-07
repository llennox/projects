# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-22 17:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gpp', '0005_remove_photo_photourl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='photo',
            name='lat',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='photo',
            name='lon',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='photo',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='profil',
            name='dateCreated',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
