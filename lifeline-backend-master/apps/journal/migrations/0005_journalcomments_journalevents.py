# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-05-16 15:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0004_auto_20190416_1615'),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalComments',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('journal.journal',),
        ),
        migrations.CreateModel(
            name='JournalEvents',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('journal.journal',),
        ),
    ]
