# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-19 08:54
from __future__ import unicode_literals

from django.contrib.auth.hashers import make_password
from django.db import migrations


def createsuperuser(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.get_or_create(
        email='lifeline.product.care@gmail.com', is_superuser=True, is_active=True, is_staff=True,
        username='Admin', password=make_password('123qaz123!A')
    )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(createsuperuser, reverse_code=migrations.RunPython.noop),
    ]
