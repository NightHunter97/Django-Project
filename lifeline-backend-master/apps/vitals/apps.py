from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class VitalsConfig(AppConfig):
    name = 'apps.vitals'
    verbose_name = _('Vitals')
    icon = '<i class="material-icons">control_point</i>'
