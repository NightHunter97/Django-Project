from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class JournalConfig(AppConfig):
    name = 'apps.journal'
    verbose_name = _('Journal')
    icon = '<i class="material-icons">local_library</i>'
