# Generated by Django 2.1.4 on 2019-01-26 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0005_auto_20190114_0832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventparticipant',
            name='participant_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Employee'), (1, 'Customer'), (2, 'Vendor')]),
        ),
    ]