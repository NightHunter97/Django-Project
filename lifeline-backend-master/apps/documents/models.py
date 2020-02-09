from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from lifeline.storage_backends import PrivateMediaStorage
from apps.patients.models import Patient, File
from django_extensions.db.models import TimeStampedModel
from django.core.files.storage import FileSystemStorage


class DocumentType(models.Model):
    name = models.CharField(_('Document Type'), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Document Type')
        verbose_name_plural = _('Documents Types')
        db_table = 'document_type'
        ordering = ('name',)

class Document(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    patient_file = models.ForeignKey(File, on_delete=models.CASCADE, blank=True, null=True)
    file = models.FileField(storage=PrivateMediaStorage())
    name = models.CharField(_('documents name'), max_length=64)
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, blank=False)
    extension = models.CharField(_('documents extension'), max_length=64, blank=True)

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        db_table = 'documents'
