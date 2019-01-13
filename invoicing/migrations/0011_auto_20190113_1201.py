# Generated by Django 2.1.4 on 2019-01-13 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0010_salesinvoiceline_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesinvoiceline',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=9),
        ),
        migrations.AlterField(
            model_name='salesinvoiceline',
            name='value',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=9),
        ),
    ]
