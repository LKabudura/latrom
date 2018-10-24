# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-06 12:18
from __future__ import unicode_literals

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
        ('common_data', '0001_initial'),
        ('inventory', '0001_initial'),
        ('services', '0001_initial'),
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractSale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('quotation', 'Quotation'), ('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid In Full'), ('paid-partially', 'Paid Partially'), ('reversed', 'Reversed')], max_length=16)),
                ('active', models.BooleanField(default=True)),
                ('due', models.DateField(default=django.utils.timezone.now)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('terms', models.CharField(blank=True, max_length=128)),
                ('comments', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='BillLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expense', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.Expense')),
            ],
        ),
        migrations.CreateModel(
            name='CombinedInvoiceLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line_type', models.PositiveSmallIntegerField(choices=[(1, 'item'), (2, 'service'), (3, 'expense')])),
                ('quantity_or_hours', models.DecimalField(decimal_places=2, default=0.0, max_digits=9)),
                ('expense', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Expense')),
                ('item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.Item')),
                ('service', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='services.Service')),
            ],
        ),
        migrations.CreateModel(
            name='CreditNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('comments', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_address', models.TextField(blank=True, default='')),
                ('banking_details', models.TextField(blank=True, default='')),
                ('active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Account')),
                ('individual', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common_data.Individual')),
                ('organization', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common_data.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_for', models.PositiveSmallIntegerField(choices=[(0, 'Sales'), (1, 'Service'), (2, 'Bill'), (3, 'Combined')])),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('date', models.DateField()),
                ('method', models.CharField(choices=[('cash', 'Cash'), ('transfer', 'Transfer'), ('debit card', 'Debit Card'), ('ecocash', 'EcoCash')], default='transfer', max_length=32)),
                ('reference_number', models.AutoField(primary_key=True, serialize=False)),
                ('comments', models.TextField(default='Thank you for your business')),
            ],
        ),
        migrations.CreateModel(
            name='SalesConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_invoice_comments', models.TextField(blank=True)),
                ('default_quotation_comments', models.TextField(blank=True)),
                ('default_credit_note_comments', models.TextField(blank=True)),
                ('default_terms', models.TextField(blank=True)),
                ('include_shipping_address', models.BooleanField(default=False)),
                ('business_address', models.TextField(blank=True)),
                ('logo', models.ImageField(null=True, upload_to='logo/')),
                ('document_theme', models.IntegerField(choices=[(1, 'Simple'), (2, 'Blue'), (3, 'Steel'), (4, 'Verdant'), (5, 'Warm')])),
                ('currency', models.CharField(choices=[('$', 'Dollars($)'), ('R', 'Rand')], max_length=1)),
                ('apply_price_multiplier', models.BooleanField(default=False)),
                ('price_multiplier', models.FloatField(default=0.0)),
                ('business_name', models.CharField(max_length=255)),
                ('payment_details', models.TextField(blank=True)),
                ('contact_details', models.TextField(blank=True)),
                ('include_tax_in_invoice', models.BooleanField(default=True)),
                ('business_registration_number', models.CharField(blank=True, max_length=32)),
                ('sales_tax', models.ForeignKey(blank='True', null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Tax')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SalesInvoiceLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField(default=0.0)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=4)),
                ('returned_quantity', models.FloatField(default=0.0)),
                ('returned', models.BooleanField(default=False)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Item')),
            ],
        ),
        migrations.CreateModel(
            name='SalesRepresentative',
            fields=[
                ('number', models.AutoField(primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=True)),
                ('employee', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceInvoiceLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hours', models.DecimalField(decimal_places=2, max_digits=6)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.Service')),
            ],
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('abstractsale_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='invoicing.AbstractSale')),
                ('customer_reference', models.CharField(blank=True, max_length=255)),
            ],
            bases=('invoicing.abstractsale',),
        ),
        migrations.CreateModel(
            name='CombinedInvoice',
            fields=[
                ('abstractsale_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='invoicing.AbstractSale')),
            ],
            bases=('invoicing.abstractsale',),
        ),
        migrations.CreateModel(
            name='SalesInvoice',
            fields=[
                ('abstractsale_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='invoicing.AbstractSale')),
                ('purchase_order_number', models.CharField(blank=True, max_length=32)),
                ('ship_from', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inventory.WareHouse')),
            ],
            bases=('invoicing.abstractsale',),
        ),
        migrations.CreateModel(
            name='ServiceInvoice',
            fields=[
                ('abstractsale_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='invoicing.AbstractSale')),
            ],
            bases=('invoicing.abstractsale',),
        ),
        migrations.AddField(
            model_name='payment',
            name='sales_rep',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoicing.SalesRepresentative'),
        ),
        migrations.AddField(
            model_name='abstractsale',
            name='customer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='invoicing.Customer'),
        ),
        migrations.AddField(
            model_name='abstractsale',
            name='salesperson',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='invoicing.SalesRepresentative'),
        ),
        migrations.AddField(
            model_name='abstractsale',
            name='tax',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Tax'),
        ),
        migrations.AddField(
            model_name='serviceinvoiceline',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoicing.ServiceInvoice'),
        ),
        migrations.AddField(
            model_name='salesinvoiceline',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoicing.SalesInvoice'),
        ),
        migrations.AddField(
            model_name='payment',
            name='bill',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='invoicing.Bill'),
        ),
        migrations.AddField(
            model_name='payment',
            name='combined_invoice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='invoicing.CombinedInvoice'),
        ),
        migrations.AddField(
            model_name='payment',
            name='sales_invoice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='invoicing.SalesInvoice'),
        ),
        migrations.AddField(
            model_name='payment',
            name='service_invoice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='invoicing.ServiceInvoice'),
        ),
        migrations.AddField(
            model_name='creditnote',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoicing.SalesInvoice'),
        ),
        migrations.AddField(
            model_name='combinedinvoiceline',
            name='invoice',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='invoicing.CombinedInvoice'),
        ),
        migrations.AddField(
            model_name='billline',
            name='bill',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoicing.Bill'),
        ),
    ]
