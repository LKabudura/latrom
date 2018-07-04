# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-01 17:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0012_auto_20180701_1834'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessCustomer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('tax_clearance', models.CharField(max_length=64)),
                ('business_address', models.TextField()),
                ('billing_address', models.TextField()),
                ('contact_person', models.CharField(max_length=64)),
                ('active', models.BooleanField(default=True)),
                ('website', models.CharField(max_length=64)),
                ('email', models.CharField(max_length=64)),
                ('phone', models.CharField(max_length=64)),
            ],
        ),
        migrations.AlterField(
            model_name='invoice',
            name='comments',
            field=models.TextField(blank=True, default='some default comment'),
        ),
    ]