# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-23 14:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wounds', '0003_auto_20181023_1448'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evolution',
            name='height_t',
        ),
        migrations.RemoveField(
            model_name='evolution',
            name='width_t',
        ),
    ]