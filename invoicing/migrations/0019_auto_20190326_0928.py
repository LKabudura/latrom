# Generated by Django 2.1.4 on 2019-03-26 07:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0018_auto_20190326_0927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditnoteline',
            name='line',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoicing.InvoiceLine'),
        ),
    ]
