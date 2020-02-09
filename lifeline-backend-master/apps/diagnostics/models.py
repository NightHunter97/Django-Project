from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _

from apps.diagnostics.choices import FILE_TYPE
from apps.diagnostics.validators import file_extension_validator
from lifeline.storage_backends import PrivateMediaStorage


class DiagnosticFile(TimeStampedModel):
    file = models.FileField(
        _('Uploaded file'), storage=PrivateMediaStorage(), max_length=255, null=True, blank=True,
        validators=[file_extension_validator]
    )
    label = models.CharField(_('File type'), choices=FILE_TYPE, max_length=12)
    is_uploaded = models.BooleanField(_('File was parsed successfully'), default=False)
    errors = models.TextField(_('Errors from last parsing'), null=True)

    class Meta:
        verbose_name = _('Diagnostic File')
        verbose_name_plural = _('Diagnostic Files')
        db_table = 'diagnostic_files'

    def __str__(self):
        return self.get_label_display()

    def save(self, **kwargs):
        self.is_uploaded = kwargs.pop('is_uploaded', False)
        return super().save(**kwargs)


class Diagnose(models.Model):
    concept_id = models.CharField(_('Concept ID'), max_length=100)
    term = models.CharField(_('Name'), max_length=255)

    class Meta:
        verbose_name = _('Diagnose')
        verbose_name_plural = _('Diagnoses')
        db_table = 'diagnoses'

    def __str__(self):
        return self.term


class HealthScreening(models.Model):
    term = models.CharField(_('Particular monitoring type'), max_length=100)

    class Meta:
        verbose_name = _('Health Screening')
        verbose_name_plural = _('Health Screenings')
        db_table = 'health_screening'

    def __str__(self):
        return self.term


class Diagnostic(TimeStampedModel):
    diagnose = models.ForeignKey(
        'Diagnose', verbose_name=_('Diagnose'), on_delete=models.CASCADE, blank=True, null=True
    )
    screening = models.ForeignKey(
        'HealthScreening', verbose_name=_('Health Screening'), on_delete=models.CASCADE, blank=True, null=True
    )
    creator = models.CharField(_('Creator'), max_length=255)
    user = models.ForeignKey('accounts.User', verbose_name=_('Creator'), on_delete=models.CASCADE, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    type = models.CharField(_('Type'), choices=FILE_TYPE, max_length=10)
    is_allergy = models.BooleanField(_('Is allergy'), default=False)
    file = models.ForeignKey(
        'patients.File', verbose_name=_('File'), on_delete=models.CASCADE, null=True, blank=True
    )

    @property
    def is_screening(self):
        return self.type == 'screening'

    class Meta:
        verbose_name = _('Diagnostic')
        verbose_name_plural = _('Diagnostics')
        db_table = 'diagnostics'
        ordering = ('-created',)

    def __str__(self):
        if self.diagnose:
            return self.diagnose.term
        elif self.screening:
            return self.screening.term
        return f'Diagnostic {self.pk}'


class Diagnoses(Diagnostic):
    class Meta:
        proxy = True


class Screenings(Diagnostic):
    class Meta:
        proxy = True


class Anamnesis(Diagnostic):
    class Meta:
        proxy = True
