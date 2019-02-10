# Generated by Django 2.1.4 on 2019-02-01 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0021_auto_20190201_1345'),
        ('common_data', '0005_auto_20190104_2114'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalconfig',
            name='business_address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='globalconfig',
            name='business_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='globalconfig',
            name='business_registration_number',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
        migrations.AddField(
            model_name='globalconfig',
            name='contact_details',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='globalconfig',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounting.Currency'),
        ),
        migrations.AddField(
            model_name='globalconfig',
            name='document_theme',
            field=models.IntegerField(choices=[(1, 'Simple'), (2, 'Blue'), (3, 'Steel'), (4, 'Verdant'), (5, 'Warm')], default=1),
        ),
        migrations.AddField(
            model_name='globalconfig',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='logo/'),
        ),
        migrations.AddField(
            model_name='globalconfig',
            name='payment_details',
            field=models.TextField(blank=True, default=''),
        ),
    ]