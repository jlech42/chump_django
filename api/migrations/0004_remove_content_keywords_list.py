# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-12 19:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20170712_1910'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='keywords_list',
        ),
    ]
