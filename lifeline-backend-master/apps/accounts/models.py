import uuid

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from apps.accounts import choices
from apps.accounts.managers import AccountManager


class User(AbstractUser):
    username = models.CharField(_('Username'), blank=True, null=True, max_length=255)
    phone = models.CharField(_('Mobile'), max_length=255, blank=True, null=True)
    line = models.CharField(_('Direct line'), max_length=255, blank=True, null=True)
    inami = models.CharField(
        _('INAMI number (accredited number for healthcare professional) '), max_length=255, blank=True, null=True
    )
    language = models.CharField(_('User language'), max_length=16, choices=settings.LANGUAGES, default='en')
    email = models.EmailField(_('Email address'), unique=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    gender = models.CharField(_('Gender'), max_length=1, choices=choices.SEX, null=True)
    units = models.ManyToManyField('units.Unit')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = AccountManager()

    def __str__(self):
        return self.username or self.email

    def save(self, *args, **kwargs):
        self.username = f'{self.first_name} {self.last_name}'.strip() \
            if self.first_name or self.last_name else self.email
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'
        ordering = ('date_joined',)


class Activity(TimeStampedModel):
    user = models.CharField(_('Username'), max_length=255)
    email = models.CharField(_('User email'), max_length=255)
    file_id = models.CharField(_('Patient file id'), max_length=255, null=True, blank=True)
    patient = models.CharField(_('Patient name'), max_length=255, null=True, blank=True)
    patient_id = models.CharField(_('Patient id'), max_length=255, null=True, blank=True)
    activity = models.TextField(blank=True, null=True)
    data = models.TextField(_('Data'), null=True)

    class Meta:
        verbose_name = _('User activity')
        verbose_name_plural = _('Users activities')
        db_table = 'user_activities'
        ordering = ('-created',)


class AdminActivity(models.Model):
    log_entry = models.ForeignKey(
        'admin.LogEntry', verbose_name=_('LogEntry'), on_delete=models.CASCADE, null=True
    )
    patient_id = models.CharField(_('Patient id'), max_length=16)

    class Meta:
        verbose_name = _('Admin User activity')
        verbose_name_plural = _('Admin Users activities')
        db_table = 'admin_activities'
