# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-09-10 12:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0021_auto_20190910_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prescription',
            name='cycle_every_reccurence',
            field=models.CharField(blank=True, choices=[('DAYS', 'Days'), ('WEEKS', 'Weeks'), ('MONTHS', 'Months')], max_length=6, null=True, verbose_name='Reccurence'),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='cycle_every_value',
            field=models.IntegerField(blank=True, null=True, verbose_name='Every'),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='cycle_over_reccurence',
            field=models.CharField(blank=True, choices=[('DAYS', 'Days'), ('WEEKS', 'Weeks'), ('MONTHS', 'Months')], max_length=6, null=True, verbose_name='Reccurence'),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='cycle_over_value',
            field=models.IntegerField(blank=True, null=True, verbose_name='Value'),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='duration',
            field=models.CharField(blank=True, choices=[('INDEF', 'Indefinite'), ('FIXED', 'Fixed')], max_length=5, null=True, verbose_name='Duration'),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='meal',
            field=models.CharField(blank=True, choices=[('BEFORE', 'Before'), ('AFTER', 'After')], max_length=6, null=True, verbose_name='Meal'),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='mode',
            field=models.CharField(blank=True, choices=[('DAYLI', 'Daily'), ('CONDITIONAL', 'Conditional')], max_length=11, null=True, verbose_name='type'),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='repeat_every',
            field=models.IntegerField(blank=True, null=True, verbose_name='Every'),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='repeat_reccurence',
            field=models.CharField(blank=True, choices=[('DAYS', 'Days'), ('WEEKS', 'Weeks'), ('MONTHS', 'Months')], max_length=6, null=True, verbose_name='Reccurence'),
        ),
    ]
