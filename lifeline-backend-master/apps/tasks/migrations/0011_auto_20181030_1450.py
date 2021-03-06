# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-30 14:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0001_initial'),
        ('tasks', '0010_schedule_wound'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='prescription',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='medications.Prescription', verbose_name='Prescription'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task', to='tasks.Task', verbose_name='Task'),
        ),
    ]
