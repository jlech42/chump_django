# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-15 22:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20170714_0249'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='test',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
    ]
