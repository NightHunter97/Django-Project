from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PatientsConfig(AppConfig):
    name = 'apps.patients'
    verbose_name = _('Patients')
    icon = '<i class="material-icons">contacts</i>'

    def ready(self):
        import apps.evaluations.receivers

