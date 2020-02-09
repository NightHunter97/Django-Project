from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TasksConfig(AppConfig):
    name = 'apps.tasks'
    verbose_name = _('Tasks')
    icon = '<i class="material-icons">schedule</i>'

    def ready(self):
        import apps.tasks.receivers
