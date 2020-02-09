# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from django.db import migrations

from lifeline import settings


def is_editable_false(apps, schema_editor):
    evaluations = apps.get_model('evaluations', 'Evaluation')
    for evaluation in evaluations.objects.all():
        if not evaluation.survey_results:
            evaluation.is_editable = False
            evaluation.save(update_fields=["is_editable"])


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0012_auto_20190528_0747'),
    ]

    operations = [
        migrations.RunPython(is_editable_false, reverse_code=migrations.RunPython.noop),
    ]
