# Generated by Django 2.1.1 on 2018-12-17 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0014_orderpayment_entry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='supplier',
            field=models.ForeignKey(default=1, on_delete=None, to='inventory.Supplier'),
        ),
    ]