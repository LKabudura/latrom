# Generated by Django 2.1.8 on 2019-05-31 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0008_email_server_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inbox',
            name='threads',
        ),
        migrations.RemoveField(
            model_name='inbox',
            name='user',
        ),
        migrations.RemoveField(
            model_name='message',
            name='copy',
        ),
        migrations.RemoveField(
            model_name='message',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='message',
            name='sender',
        ),
        migrations.RemoveField(
            model_name='message',
            name='thread',
        ),
        migrations.RemoveField(
            model_name='messagethread',
            name='initiator',
        ),
        migrations.RemoveField(
            model_name='messagethread',
            name='messages',
        ),
        migrations.RemoveField(
            model_name='messagethread',
            name='participants',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_sync_id',
            field=models.CharField(blank=True, default='', max_length=16),
        ),
        migrations.DeleteModel(
            name='Inbox',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
        migrations.DeleteModel(
            name='MessageThread',
        ),
    ]