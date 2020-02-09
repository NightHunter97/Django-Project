from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DiagnosticsConfig(AppConfig):
    name = 'apps.diagnostics'
    verbose_name = _('Diagnostics')
    icon = '<i class="material-icons">search</i>'
