from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BrusafeConfig(AppConfig):
    name = 'apps.brusafe'
    verbose_name = _('Brusafe')
    icon = '<i class="material-icons">add_to_queue</i>'
