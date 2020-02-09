from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _

from apps.wounds import choices
from lifeline.storage_backends import PrivateMediaStorage


class Wound(TimeStampedModel):
    name = models.CharField(_('Wound name'), max_length=255)
    type = models.CharField(_('Wound type'), choices=choices.WOUND_TYPES, max_length=255)
    localization = models.CharField(
        _('Localization'), choices=choices.LOCALIZATION, max_length=255
    )
    is_cured = models.BooleanField(default=False)
    file = models.ForeignKey('patients.File', verbose_name=_('Patient File'), on_delete=models.CASCADE, null=True)
    comment = models.TextField(null=True, blank=True)
    user = models.ForeignKey('accounts.User', verbose_name=_('Creator'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('Wound')
        verbose_name_plural = _('Wounds')
        db_table = 'wounds'
        ordering = ('-created',)

    def __str__(self):
        return self.name


class Evolution(TimeStampedModel):
    width = models.DecimalField(_('Width'), max_digits=5, decimal_places=2)
    height = models.DecimalField(_('Height'), max_digits=5, decimal_places=2)
    photo = models.ImageField(_('Wound photo'), storage=PrivateMediaStorage(), max_length=255, null=True)
    thumbnail = models.ImageField(_('Wound photo'), storage=PrivateMediaStorage(), max_length=255, null=True)
    wound = models.ForeignKey('Wound', verbose_name=_('Wound'), on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', verbose_name=_('Creator'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('Evolution')
        verbose_name_plural = _('Evolutions')
        db_table = 'wound_evolution'
        ordering = ('-created',)

    def __str__(self):
        return f'{self.width} x {self.height}'

    def save(self, *args, **kwargs):
        if self.photo:
            self._prepare_thumbnail()
        super().save(**kwargs)

    def _prepare_thumbnail(self):
        img = Image.open(self.photo)
        width, height = img.size
        if width < 250 and height < 250:
            ratio = (250, 250)
        elif width < 250:
            ratio = (250, int(250/(width/height)))
        else:
            ratio = (int(250*(width/height)), 250)
        resized = img.resize(ratio, Image.ANTIALIAS)
        new_image_io = BytesIO()
        if img.format == 'JPEG':
            resized.save(new_image_io, format='JPEG')
        elif img.format == 'PNG':
            resized.save(new_image_io, format='PNG')

        self.thumbnail.save(
            f'thumb_{self.photo.name}',
            content=ContentFile(new_image_io.getvalue()),
            save=False
        )
