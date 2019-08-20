# Generated by Django 2.1.8 on 2019-08-12 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_auto_20190723_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumablesrequisition',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employees.Department'),
        ),
        migrations.AlterField(
            model_name='equipmentrequisition',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employees.Department'),
        ),
    ]