# Generated by Django 2.1.8 on 2019-08-14 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0021_auto_20190623_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bubble',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='C:\\Users\\Conrad\\Documents\\code\\latrom\\media\\messaging'),
        ),
        migrations.AlterField(
            model_name='email',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='C:\\Users\\Conrad\\Documents\\code\\latrom\\media\\messaging'),
        ),
        migrations.AlterField(
            model_name='email',
            name='created_timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='icon',
            field=models.ImageField(null=True, upload_to='C:\\Users\\Conrad\\Documents\\code\\latrom\\media\\chat'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='C:\\Users\\Conrad\\Documents\\code\\latrom\\media\\chat'),
        ),
    ]
