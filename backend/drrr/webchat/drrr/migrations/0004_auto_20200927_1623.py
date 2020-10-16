# Generated by Django 3.1.1 on 2020-09-27 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drrr', '0003_users_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='host_nickname',
            field=models.CharField(default='john due', max_length=50),
        ),
        migrations.AddField(
            model_name='users',
            name='channel_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
