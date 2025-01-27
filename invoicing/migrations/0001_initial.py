# Generated by Django 2.1 on 2019-10-14 05:59

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common_data', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('comments', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CreditNoteLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('billing_address', models.TextField(blank=True, default='')),
                ('banking_details', models.TextField(blank=True, default='')),
                ('individual', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common_data.Individual')),
                ('organization', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common_data.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('quotation', 'Quotation'), ('proforma', 'Proforma Invoice'), ('invoice', 'Invoice'), ('paid', 'Paid In Full'), ('paid-partially', 'Paid Partially')], max_length=16)),
                ('invoice_number', models.PositiveIntegerField(null=True)),
                ('quotation_number', models.PositiveIntegerField(null=True)),
                ('quotation_date', models.DateField(blank=True, null=True)),
                ('quotation_valid', models.DateField(blank=True, null=True)),
                ('draft', models.BooleanField(blank=True, default=True)),
                ('salesperson', models.CharField(max_length=64)),
                ('due', models.DateField(default=datetime.date.today)),
                ('date', models.DateField(default=datetime.date.today)),
                ('terms', models.CharField(blank=True, max_length=128)),
                ('comments', models.TextField(blank=True)),
                ('purchase_order_number', models.CharField(blank=True, max_length=32)),
                ('customer', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoicing.Customer')),
                ('invoice_validated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('ship_from', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.WareHouse')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InvoiceLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line_type', models.PositiveSmallIntegerField(choices=[(1, 'product'), (2, 'service')])),
                ('tax', models.FloatField(default=0.0)),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
                ('invoice', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoicing.Invoice')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('active', models.BooleanField(default=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=16)),
                ('date', models.DateField()),
                ('method', models.CharField(choices=[('cash', 'Cash'), ('transfer', 'Transfer'), ('debit card', 'Debit Card'), ('ecocash', 'EcoCash')], default='transfer', max_length=32)),
                ('reference_number', models.AutoField(primary_key=True, serialize=False)),
                ('sales_rep', models.CharField(max_length=64)),
                ('comments', models.TextField(default='Thank you for your business')),
                ('invoice', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoicing.Invoice')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductLineComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('returned', models.BooleanField(default=False)),
                ('unit_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
                ('value', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
                ('quantity', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.InventoryItem')),
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
                ('sales_tax', models.FloatField(default=0.0)),
                ('include_shipping_address', models.BooleanField(default=False)),
                ('include_tax_in_invoice', models.BooleanField(default=True)),
                ('include_units_in_sales_invoice', models.BooleanField(default=True)),
                ('next_invoice_number', models.IntegerField(default=1)),
                ('next_quotation_number', models.IntegerField(default=1)),
                ('use_sales_invoice', models.BooleanField(default=True)),
                ('use_service_invoice', models.BooleanField(default=True)),
                ('use_bill_invoice', models.BooleanField(default=True)),
                ('use_combined_invoice', models.BooleanField(default=True)),
                ('is_configured', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceLineComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(max_length=255)),
                ('hours', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
                ('flat_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
                ('hourly_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
            ],
        ),
        migrations.AddField(
            model_name='invoiceline',
            name='product',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoicing.ProductLineComponent'),
        ),
        migrations.AddField(
            model_name='invoiceline',
            name='service',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoicing.ServiceLineComponent'),
        ),
        migrations.AddField(
            model_name='creditnoteline',
            name='line',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoicing.InvoiceLine'),
        ),
        migrations.AddField(
            model_name='creditnoteline',
            name='note',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoicing.CreditNote'),
        ),
        migrations.AddField(
            model_name='creditnote',
            name='invoice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoicing.Invoice'),
        ),
    ]
