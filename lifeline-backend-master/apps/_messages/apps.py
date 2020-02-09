from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class MessagesConfig(AppConfig):
    name = 'apps._messages'
    verbose_name = _('Messages')
    icon = '<i class="material-icons">mail_outline</i>'
