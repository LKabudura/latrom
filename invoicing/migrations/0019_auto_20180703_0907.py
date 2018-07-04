# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-03 07:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0018_auto_20180702_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='comments',
            field=models.TextField(blank=True, default='Thank you for your business'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='terms',
            field=models.CharField(default='Pay strictly in 7 days', max_length=64),
        ),
    ]