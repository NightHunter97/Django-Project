from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from apps.reports import choices

from lifeline.storage_backends import PrivateMediaStorage


class Report(TimeStampedModel):
    title = models.CharField(_('Title'), max_length=255)
    file = models.ForeignKey('patients.File', verbose_name=_('File'), on_delete=models.CASCADE, null=True, blank=True)
    report = models.FileField(_('Report'), upload_to='reports/', storage=PrivateMediaStorage(), max_length=255)
    type = models.CharField(choices=choices.REPORT_TYPE, max_length=10)
    creator = models.ForeignKey('accounts.User', verbose_name=_('Creator'), on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        db_table = 'reports'
        ordering = ('-created',)

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        from apps.reports.services import get_current_time_zone_datetime
        if not self.title:
            date_time = get_current_time_zone_datetime()
            self.title = f'{date_time.strftime("%d %m %Y, %H:%M")} / {self.creator.username}'
        return super().save(**kwargs)


class Logo(models.Model):
    image = models.ImageField(_('Logo'))

    class Meta:
        verbose_name = _('Report Logo')
        verbose_name_plural = _('Report Logos')
        db_table = 'logos'
