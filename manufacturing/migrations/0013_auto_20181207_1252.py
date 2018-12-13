# Generated by Django 2.1.1 on 2018-12-07 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manufacturing', '0012_auto_20181207_1226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='process',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='process',
            name='rate',
            field=models.ForeignKey(blank=True, null=True, on_delete=None, to='manufacturing.ProcessRate'),
        ),
        migrations.AlterField(
            model_name='processrate',
            name='quantity',
            field=models.FloatField(default=0.0),
        ),
    ]
