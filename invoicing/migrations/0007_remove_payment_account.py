# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-26 20:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0006_auto_20180622_2130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='account',
        ),
    ]