# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-11 09:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('_messages', '0003_aboutpatient'),
    ]

    operations = [
        migrations.RenameField(
            model_name='aboutpatient',
            old_name='created_by',
            new_name='user',
        ),
    ]
