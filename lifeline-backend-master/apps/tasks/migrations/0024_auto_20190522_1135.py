# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-05-22 11:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0023_auto_20190522_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='icon',
            field=models.CharField(blank=True, choices=[('tasks/icons/accompaniment-appointments-and-procedures.svg', 'Accompaniment, Appointments and Procedures'), ('tasks/icons/assessment-and-protection.svg', 'Assessment and Protection'), ('tasks/icons/basic-nursing-care.svg', 'Basic nursing care'), ('tasks/icons/physio-treatment.svg', 'Physio Treatment'), ('tasks/icons/psychol-care.svg', 'Psycho care'), ('tasks/icons/relational-treatment-and-care.svg', 'Relational treatment and care'), ('tasks/icons/sa-monitoring.svg', 'SA monitoring'), ('tasks/icons/sample.svg', 'Sample'), ('tasks/icons/technical-act.svg', 'Technical act'), ('tasks/icons/therapeutic-activity.svg', 'Therapeutic activity'), ('tasks/icons/therapeutic-education.svg', 'Therapeutic education'), ('tasks/icons/medication.svg', 'Medication')], max_length=255, null=True, verbose_name='Static Icon'),
        ),
    ]
