# Generated by Django 5.1.4 on 2025-04-05 09:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_customuser_last_seen'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='online_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_seen',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2025, 4, 5, 12, 39, 0, 403958), null=True),
        ),
    ]
