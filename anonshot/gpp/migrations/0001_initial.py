# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-08 21:06
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photouuid', models.UUIDField(default=None)),
                ('comment', models.CharField(max_length=255)),
                ('postedByuuid', models.UUIDField(default=None)),
                ('date', models.DateTimeField(default=None, null=True)),
                ('active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('photoURL', models.URLField(default=None)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('lat', models.FloatField(default=0)),
                ('lon', models.FloatField(default=0)),
                ('poster', models.UUIDField(default=None)),
                ('timestamp', models.DateTimeField(default=None, null=True)),
                ('visible', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profil',
            fields=[
                ('activation_key', models.CharField(max_length=40)),
                ('key_expires', models.DateTimeField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('dateCreated', models.DateTimeField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profil', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
