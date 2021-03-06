# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-09 13:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0011_archivecomment'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmergencyContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relation', models.CharField(blank=True, choices=[('M', 'Mother'), ('F', 'Father'), ('W', 'Wife')], max_length=128, null=True, verbose_name='Relation')),
                ('name', models.CharField(blank=True, max_length=128, null=True, verbose_name='Name')),
                ('phone', models.CharField(max_length=255, verbose_name='Phone')),
                ('email', models.EmailField(blank=True, max_length=128, null=True, verbose_name='E-mail Address')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.Patient', verbose_name='File')),
            ],
            options={
                'verbose_name': 'Emergency Contact',
                'verbose_name_plural': 'Emergency Contacts',
                'db_table': 'emergency_contacts',
            },
        ),
    ]
