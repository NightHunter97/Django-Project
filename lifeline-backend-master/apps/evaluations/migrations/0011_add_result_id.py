# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from django.db import migrations

from lifeline import settings


def add_result_id(apps, schema_editor):
    evaluations = apps.get_model('evaluations', 'Evaluation')
    for name in evaluations.objects.values_list('name', flat=True):
        index = 1
        for evaluation in evaluations.objects.filter(name=name).order_by('-created'):
            evaluation.results_id = index
            evaluation.save(update_fields=["results_id"])
            index += 1


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0010_evaluation_is_editable'),
    ]

    operations = [
        migrations.RunPython(add_result_id, reverse_code=migrations.RunPython.noop),
    ]
