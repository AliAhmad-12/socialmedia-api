# Generated by Django 5.0.1 on 2025-04-15 16:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alter_customuser_last_seen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='last_seen',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2025, 4, 15, 19, 47, 44, 717153), null=True),
        ),
    ]
