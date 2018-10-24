# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-06 12:18
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Allowance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('amount', models.FloatField()),
                ('active', models.BooleanField(default=True)),
                ('taxable', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CommissionRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('min_sales', models.FloatField()),
                ('rate', models.FloatField()),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Deduction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('method', models.IntegerField(choices=[(0, 'Rated'), (1, 'Fixed')])),
                ('trigger', models.IntegerField(choices=[(0, 'All Income'), (1, 'Taxable Income'), (2, 'Tax')], default=0)),
                ('rate', models.FloatField(default=0)),
                ('amount', models.FloatField(default=0)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('first_name', models.CharField(max_length=32)),
                ('last_name', models.CharField(max_length=32)),
                ('address', models.TextField(blank=True, default='', max_length=128)),
                ('email', models.CharField(blank=True, default='', max_length=32)),
                ('phone', models.CharField(blank=True, default='', max_length=16)),
                ('employee_number', models.AutoField(primary_key=True, serialize=False)),
                ('hire_date', models.DateField()),
                ('title', models.CharField(max_length=32)),
                ('leave_days', models.FloatField(default=0)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmployeesSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payroll_date_one', models.PositiveSmallIntegerField()),
                ('payroll_date_two', models.PositiveSmallIntegerField()),
                ('payroll_date_three', models.PositiveSmallIntegerField()),
                ('payroll_date_four', models.PositiveSmallIntegerField()),
                ('payroll_cycle', models.CharField(choices=[('weekly', 'Weekly'), ('bi-monthly', 'Bi-monthly'), ('monthly', 'Monthly')], max_length=12)),
                ('require_verification_before_posting_payslips', models.BooleanField(default=True)),
                ('salary_follows_profits', models.BooleanField(default=True)),
                ('automate_payroll_for', models.ManyToManyField(to='employees.Employee')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PayGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('monthly_salary', models.FloatField(default=0)),
                ('monthly_leave_days', models.FloatField(default=0)),
                ('hourly_rate', models.FloatField(default=0)),
                ('overtime_rate', models.FloatField(default=0)),
                ('overtime_two_rate', models.FloatField(default=0)),
                ('allowances', models.ManyToManyField(blank=True, to='employees.Allowance')),
                ('commission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.CommissionRule')),
                ('deductions', models.ManyToManyField(blank=True, to='employees.Deduction')),
            ],
        ),
        migrations.CreateModel(
            name='PayrollTax',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('paid_by', models.IntegerField(choices=[(0, 'Employees'), (1, 'Employer')])),
            ],
        ),
        migrations.CreateModel(
            name='Payslip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_period', models.DateField()),
                ('end_period', models.DateField()),
                ('normal_hours', models.FloatField()),
                ('overtime_one_hours', models.FloatField()),
                ('overtime_two_hours', models.FloatField()),
                ('pay_roll_id', models.IntegerField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='TaxBracket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lower_boundary', models.DecimalField(decimal_places=2, max_digits=9)),
                ('upper_boundary', models.DecimalField(decimal_places=2, max_digits=9)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('deduction', models.DecimalField(decimal_places=2, max_digits=9)),
                ('payroll_tax', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.PayrollTax')),
            ],
        ),
        migrations.AddField(
            model_name='paygrade',
            name='payroll_taxes',
            field=models.ManyToManyField(blank=True, to='employees.PayrollTax'),
        ),
        migrations.AddField(
            model_name='employee',
            name='pay_grade',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='employees.PayGrade'),
        ),
        migrations.AddField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
