# Generated by Django 2.1.1 on 2018-12-18 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0011_deduction_account_paid_into'),
    ]

    operations = [
        migrations.AddField(
            model_name='payslip',
            name='pay_grade',
            field=models.ForeignKey(default=1, on_delete=None, to='employees.PayGrade'),
        ),
    ]
