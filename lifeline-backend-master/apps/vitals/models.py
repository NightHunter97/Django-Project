from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _

from apps.vitals import choices


class VitalsParam(TimeStampedModel):
    type = models.CharField(verbose_name=_('Type'), choices=choices.VITAL_TYPES, max_length=10)
    user = models.ForeignKey('accounts.User', verbose_name=_('Doctor'), on_delete=models.CASCADE)
    file = models.ForeignKey('patients.File', verbose_name=_('Patient File'), on_delete=models.CASCADE)
    value = models.CharField(max_length=255, verbose_name=_('Value'))
    comment = models.TextField(verbose_name=_('Comment'), null=True, blank=True)

    class Meta:
        verbose_name = _('Vitals Parameter')
        verbose_name_plural = _('Vitals Parameters')
        db_table = 'vitals_param'
        ordering = ('-created',)

    def __str__(self):
        return self.type
