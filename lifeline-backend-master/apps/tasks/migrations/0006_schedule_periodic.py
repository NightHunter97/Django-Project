# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-19 13:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0005_auto_20181016_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='periodic',
            field=models.CharField(blank=True, choices=[('DAY', 'Daily'), ('WEEK', 'Weekly'), ('MONTH', 'Monthly'), ('YEAR', 'Yearly')], max_length=5, null=True, verbose_name='Task periodic'),
        ),
    ]