# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-16 19:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0015_auto_20180816_0659'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventorysettings',
            name='use_storage_media_model',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='inventorysettings',
            name='use_warehousing_model',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='storagemedia',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='transferorder',
            name='issuing_inventory_controller',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='issuing_inventory_controller', to='employees.Employee'),
        ),
        migrations.AlterField(
            model_name='transferorder',
            name='receiving_inventory_controller',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.Employee'),
        ),
    ]
