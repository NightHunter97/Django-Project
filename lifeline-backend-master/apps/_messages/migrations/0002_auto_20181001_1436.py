# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-01 14:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('_messages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='msg_content',
            field=models.TextField(),
        ),
    ]
