# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-08 15:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0016_auto_20180706_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credit',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=9),
        ),
        migrations.AlterField(
            model_name='debit',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=9),
        ),
    ]