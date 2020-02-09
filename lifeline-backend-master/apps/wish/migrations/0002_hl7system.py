# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-06-20 09:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wish', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HL7System',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('os', models.UUIDField(verbose_name='Operating system uuid')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='systems', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'HL7 Operating System',
                'verbose_name_plural': 'HL7 Operating Systems',
                'db_table': 'hl7_systems',
                'ordering': ('-created',),
            },
        ),
    ]