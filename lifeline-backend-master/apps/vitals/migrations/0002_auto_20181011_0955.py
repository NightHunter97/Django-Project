# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-11 09:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vitals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vitalsparam',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Comment'),
        ),
    ]
