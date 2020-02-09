from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class WishConfig(AppConfig):
    name = 'apps.wish'
    verbose_name = _('Wish')
    icon = '<i class="material-icons">add_to_queue</i>'
