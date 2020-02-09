# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-03-11 16:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0005_auto_20181210_1537'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('term',), 'verbose_name': 'Medication Category', 'verbose_name_plural': 'Medication Categories'},
        ),
        migrations.RenameField(
            model_name='category',
            old_name='name',
            new_name='term',
        ),
        migrations.AddField(
            model_name='category',
            name='code',
            field=models.CharField(default='code', max_length=64, verbose_name='Code'),
        ),
        migrations.AddField(
            model_name='category',
            name='dosage',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='Dosage'),
        ),
        migrations.AddField(
            model_name='category',
            name='unit',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='Unit'),
        ),
        migrations.AddField(
            model_name='category',
            name='vmp_code',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='VMP Code'),
        ),
    ]
