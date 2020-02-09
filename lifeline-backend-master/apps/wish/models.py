from django.db import models
from django_extensions.db.models import TimeStampedModel

from django.utils.translation import ugettext_lazy as _


class HL7System(TimeStampedModel):
    user = models.ForeignKey(
        'accounts.User',
        verbose_name=_('User'),
        related_name='systems',
        on_delete=models.CASCADE,
        null=True
    )
    os = models.UUIDField(verbose_name=_('Operating system uuid'))

    class Meta:
        verbose_name = _('HL7 Operating System')
        verbose_name_plural = _('HL7 Operating Systems')
        db_table = 'hl7_systems'
        ordering = ('-created',)
