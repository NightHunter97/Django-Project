from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from django.db import models

from lifeline.storage_backends import PrivateMediaStorage


class Message(TimeStampedModel):
    sender = models.ForeignKey(
        'accounts.User', verbose_name=_('Sender'), related_name="sender",
        null=True, blank=True, on_delete=models.CASCADE
    )
    message_from = models.CharField(_('Message From'), max_length=255)
    message_to = JSONField(_('Message To'))
    receivers = models.ManyToManyField('accounts.User', verbose_name=_('Receivers'), related_name="receivers")
    subject = models.CharField(_('Subject'), max_length=255, db_index=True)
    msg_content = models.TextField()
    read_by = ArrayField(models.CharField(max_length=36), null=True, blank=True, default=[])

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        db_table = 'messages'
        ordering = ('-created',)


class MessageFile(models.Model):
    message = models.ForeignKey(Message, verbose_name=_('Message File'), related_name='message_file')
    file = models.FileField(_('Uploaded file'), storage=PrivateMediaStorage(), max_length=255)

    class Meta:
        verbose_name = _('Message File')
        verbose_name_plural = _('Messages Files')
        db_table = 'message_files'


class AboutPatient(TimeStampedModel):
    subject = models.CharField(_('Subject'), max_length=255, db_index=True)
    msg_content = models.TextField()
    read_by = ArrayField(models.CharField(max_length=36), null=True, blank=True, default=[])
    file = models.ForeignKey('patients.File', verbose_name=_('Patient File'), on_delete=models.CASCADE, null=True)
    user = models.ForeignKey('accounts.User', verbose_name=_('Creator'), on_delete=models.CASCADE, null=True)
    hidden_for = ArrayField(models.CharField(max_length=36), null=True, blank=True, default=[])

    class Meta:
        verbose_name = _('About Patients Message')
        verbose_name_plural = _('About Patients Messages')
        db_table = 'about_patients_messages'
        ordering = ('-created',)
