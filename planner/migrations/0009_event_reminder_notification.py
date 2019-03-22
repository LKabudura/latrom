# Generated by Django 2.1.4 on 2019-03-19 18:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0005_auto_20190108_2030'),
        ('planner', '0008_auto_20190317_2027'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='reminder_notification',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='messaging.Notification'),
        ),
    ]