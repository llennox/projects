# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-07 05:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gpp', '0008_profil_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(default='anon', max_length=50)),
                ('reieving', models.CharField(default='anon', max_length=50)),
            ],
        ),
    ]
