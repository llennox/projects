# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-30 22:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('btc', '0005_auto_20160829_0006'),
    ]

    operations = [
        migrations.CreateModel(
            name='buyUrls',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('website', models.URLField()),
                ('mozscore', models.IntegerField(default=0)),
                ('price', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='webpage', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='escrowPayoutLedger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('escrow', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='sellUrls',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activelink', models.URLField()),
                ('website', models.URLField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='backlink', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
