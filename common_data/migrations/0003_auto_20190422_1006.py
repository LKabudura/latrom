# Generated by Django 2.1.4 on 2019-04-22 08:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common_data', '0002_auto_20190410_1137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='globalconfig',
            name='business_address',
        ),
        migrations.RemoveField(
            model_name='globalconfig',
            name='business_name',
        ),
        migrations.RemoveField(
            model_name='globalconfig',
            name='business_registration_number',
        ),
        migrations.RemoveField(
            model_name='globalconfig',
            name='contact_details',
        ),
        migrations.RemoveField(
            model_name='globalconfig',
            name='logo',
        ),
        migrations.AddField(
            model_name='globalconfig',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='common_data.Organization'),
        ),
    ]