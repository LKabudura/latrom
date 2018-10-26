# Generated by Django 2.1.1 on 2018-10-26 04:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


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
            name='AttendanceLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time_in', models.TimeField()),
                ('time_out', models.TimeField()),
                ('lunch_duration', models.DurationField()),
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
            name='EmployeeTimeSheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.PositiveSmallIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12)])),
                ('year', models.PositiveSmallIntegerField(choices=[(2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025), (2026, 2026), (2027, 2027), (2028, 2028), (2029, 2029), (2030, 2030), (2031, 2031), (2032, 2032), (2033, 2033), (2034, 2034), (2035, 2035), (2036, 2036), (2037, 2037), (2038, 2038), (2039, 2039), (2040, 2040), (2041, 2041), (2042, 2042), (2043, 2043), (2044, 2044), (2045, 2045), (2046, 2046), (2047, 2047), (2048, 2048), (2049, 2049), (2050, 2050)])),
                ('complete', models.BooleanField(default=False)),
                ('employee', models.ForeignKey(on_delete=None, related_name='target', to='employees.Employee')),
                ('recorded_by', models.ForeignKey(on_delete=None, related_name='recorder', to='employees.Employee')),
            ],
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
                ('commission', models.ForeignKey(blank=True, null=True, on_delete=None, to='employees.CommissionRule')),
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
                ('employee', models.ForeignKey(on_delete=None, to='employees.Employee')),
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
                ('payroll_tax', models.ForeignKey(on_delete=None, to='employees.PayrollTax')),
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
        migrations.AddField(
            model_name='attendanceline',
            name='timesheet',
            field=models.ForeignKey(on_delete=None, to='employees.EmployeeTimeSheet'),
        ),
    ]
