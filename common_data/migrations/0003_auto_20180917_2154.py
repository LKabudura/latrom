# Generated by Django 2.1.1 on 2018-09-17 19:54

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common_data', '0002_auto_20180825_0753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='author',
            field=models.ForeignKey(on_delete=None, to=settings.AUTH_USER_MODEL),
        ),
    ]
