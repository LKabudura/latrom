# Generated by Django 2.1.1 on 2018-09-17 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_auto_20180812_2158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credit',
            name='account',
            field=models.ForeignKey(on_delete=None, to='accounting.Account'),
        ),
        migrations.AlterField(
            model_name='debit',
            name='account',
            field=models.ForeignKey(on_delete=None, to='accounting.Account'),
        ),
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Advertising'), (1, 'Bank Service Charges'), (2, 'Equipment Rental'), (3, 'Dues and Subscriptions'), (4, 'Telephone'), (5, 'Vehicles'), (6, 'Travel and Expenses'), (7, 'Suppliers'), (8, 'Rent'), (9, 'Payroll Expenses'), (10, 'Insurance'), (11, 'Office Expenses'), (12, 'Postage'), (13, 'Other')]),
        ),
        migrations.AlterField(
            model_name='expense',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=None, to='invoicing.Customer'),
        ),
        migrations.AlterField(
            model_name='expense',
            name='debit_account',
            field=models.ForeignKey(on_delete=None, to='accounting.Account'),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='journal',
            field=models.ForeignKey(on_delete=None, to='accounting.Journal'),
        ),
        migrations.AlterField(
            model_name='recurringexpense',
            name='category',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Advertising'), (1, 'Bank Service Charges'), (2, 'Equipment Rental'), (3, 'Dues and Subscriptions'), (4, 'Telephone'), (5, 'Vehicles'), (6, 'Travel and Expenses'), (7, 'Suppliers'), (8, 'Rent'), (9, 'Payroll Expenses'), (10, 'Insurance'), (11, 'Office Expenses'), (12, 'Postage'), (13, 'Other')]),
        ),
        migrations.AlterField(
            model_name='recurringexpense',
            name='debit_account',
            field=models.ForeignKey(on_delete=None, to='accounting.Account'),
        ),
    ]
