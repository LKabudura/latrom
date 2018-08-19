# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-16 20:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
        ('inventory', '0016_auto_20180816_2150'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouse',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='warehouse',
            name='height',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='warehouse',
            name='inventory_controller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.Employee'),
        ),
        migrations.AddField(
            model_name='warehouse',
            name='length',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='warehouse',
            name='width',
            field=models.FloatField(default=0.0),
        ),
    ]
