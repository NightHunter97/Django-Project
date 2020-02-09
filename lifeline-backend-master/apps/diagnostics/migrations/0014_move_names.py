# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-29 12:39
from __future__ import unicode_literals

from django.db import migrations


def move_names(apps, schema_editor):
    diagnostic_model = apps.get_model('diagnostics', 'Diagnostic')
    diagnose_model = apps.get_model('diagnostics', 'Diagnose')
    screening_model = apps.get_model('diagnostics', 'HealthScreening')
    diagnostics = diagnostic_model.objects.filter(name__isnull=False, screening__isnull=True, diagnose__isnull=True)
    for diagnostic in diagnostics:
        d = diagnostic.name
        screening = screening_model.objects.filter(term=d).first()
        if screening:
            diagnostic.screening = screening
            diagnostic.save()
        else:
            diagnose = diagnose_model.objects.filter(term=d).first()
            if diagnose:
                diagnostic.diagnose = diagnose
                diagnostic.save()


class Migration(migrations.Migration):

    dependencies = [
        ('diagnostics', '0013_diagnostic_screening'),
    ]

    operations = [
        migrations.RunPython(move_names, reverse_code=migrations.RunPython.noop),
    ]