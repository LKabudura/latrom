# Generated by Django 2.1.1 on 2018-12-06 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manufacturing', '0007_auto_20181206_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billofmaterialsline',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=None, to='manufacturing.ProcessProduct'),
        ),
        migrations.AlterField(
            model_name='billofmaterialsline',
            name='raw_material',
            field=models.ForeignKey(blank=True, null=True, on_delete=None, to='inventory.RawMaterial'),
        ),
    ]