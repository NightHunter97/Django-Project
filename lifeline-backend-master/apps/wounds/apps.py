from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class WoundConfig(AppConfig):
    name = 'apps.wounds'
    verbose_name = _('Wounds')
    icon = '<i class="material-icons">local_pharmacy</i>'
