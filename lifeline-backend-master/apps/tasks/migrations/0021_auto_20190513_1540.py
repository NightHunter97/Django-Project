# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-05-13 15:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0020_auto_20190513_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repeatedtask',
            name='interval',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
