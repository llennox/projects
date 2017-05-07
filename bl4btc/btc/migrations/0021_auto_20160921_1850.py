# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-21 18:50
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('btc', '0020_auto_20160920_1945'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='escrowpayoutledger',
            name='id',
        ),
        migrations.RemoveField(
            model_name='escrowpayoutledger',
            name='user',
        ),
        migrations.AddField(
            model_name='escrowpayoutledger',
            name='backlink',
            field=models.URLField(default=None),
        ),
        migrations.AddField(
            model_name='escrowpayoutledger',
            name='ledgerUUID',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='escrowpayoutledger',
            name='payeeUUID',
            field=models.UUIDField(default=None),
        ),
        migrations.AddField(
            model_name='escrowpayoutledger',
            name='payerUUID',
            field=models.UUIDField(default=None),
        ),
        migrations.AddField(
            model_name='escrowpayoutledger',
            name='price',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='escrowpayoutledger',
            name='sellUrlUUID',
            field=models.UUIDField(default=None),
        ),
        migrations.AddField(
            model_name='escrowpayoutledger',
            name='timestamp',
            field=models.DateTimeField(default=None),
        ),
        migrations.AddField(
            model_name='escrowpayoutledger',
            name='timestampval',
            field=models.DateTimeField(default=None),
        ),
        migrations.AddField(
            model_name='escrowpayoutledger',
            name='timestampval30',
            field=models.DateTimeField(default=None),
        ),
    ]
