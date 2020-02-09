from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UnitsConfig(AppConfig):
    name = 'apps.units'
    verbose_name = _('Units')
    icon = '<i class="material-icons">hotel</i>'
