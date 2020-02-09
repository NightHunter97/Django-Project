from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class MedicationConfig(AppConfig):
    name = 'apps.medications'
    verbose_name = _('Medications')
    icon = '<i class="material-icons">event_note</i>'
