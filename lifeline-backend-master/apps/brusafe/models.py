from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _


class Connector(TimeStampedModel):
    user = models.ForeignKey('accounts.User', verbose_name=_('User'), on_delete=models.CASCADE, null=True)
    authenticated = models.BooleanField(verbose_name=_('Is authenticated'), default=False)
    expiration = models.DateTimeField(verbose_name='Expiration Time', null=True)

    class Meta:
        verbose_name = _('Connector')
        verbose_name_plural = _('Connectors')
        db_table = 'connectors'

    def __str__(self):
        return self.user.username


class Relation(TimeStampedModel):
    user = models.ForeignKey('accounts.User', verbose_name=_('User'), on_delete=models.CASCADE)
    patient = models.ForeignKey('patients.Patient', verbose_name=_('Patient'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Relation')
        verbose_name_plural = _('Relations')
        db_table = 'relations'
        unique_together = ('user', 'patient')

    def __str__(self):
        return f'{self.user.username} <-> {self.patient}'
