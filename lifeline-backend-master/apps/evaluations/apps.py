from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EvaluationConfig(AppConfig):
    name = 'apps.evaluations'
    verbose_name = _('Evaluations')
    icon = '<i class="material-icons">mood</i>'
