from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DocumentsConfig(AppConfig):
    name = 'apps.documents'
    verbose_name = _("Patient Documents")
    icon = '<i class="material-icons">folder_shared</i>'
