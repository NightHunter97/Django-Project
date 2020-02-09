# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-05 08:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0001_initial'),
        ('accounts', '0003_create_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1, null=True, verbose_name='Gender'),
        ),
        migrations.AddField(
            model_name='user',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='units.Unit', verbose_name='Unit'),
        ),
    ]