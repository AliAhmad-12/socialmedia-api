# Generated by Django 5.1.4 on 2025-04-13 13:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_customuser_last_seen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='last_seen',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2025, 4, 13, 16, 54, 57, 374822), null=True),
        ),
    ]
