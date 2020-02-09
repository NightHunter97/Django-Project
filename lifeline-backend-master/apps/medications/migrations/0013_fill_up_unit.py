# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-09 13:11
from __future__ import unicode_literals
from django.db import migrations


def gen_unit(apps, schema_editor):
    categorys= apps.get_model('medications', 'Category')

    for category in categorys.objects.all():
        if not category.unit:
            category.unit = "mg"
            category.save(update_fields=['unit'])


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0012_auto_20190427_0910'),
    ]

    operations = [
        migrations.RunPython(gen_unit, reverse_code=migrations.RunPython.noop),
    ]