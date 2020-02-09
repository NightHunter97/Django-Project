from django.db import models
from django.utils.translation import ugettext_lazy as _


class Unit(models.Model):
    name = models.CharField(_('Unit name'), max_length=256)
    beds = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _('Unit')
        verbose_name_plural = _('Units')
        db_table = 'units'
        ordering = ('name',)

    def __str__(self):
        return self.name
