# Generated by Django 2.1.1 on 2018-12-23 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0012_auto_20181222_1926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leave',
            name='category',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Annual Leave'), (2, 'Sick Leave'), (3, 'Study Leave'), (4, 'Maternity Leave'), (5, 'Parental Leave'), (6, 'Bereavement Leave')]),
        ),
    ]
