from django_extensions.db.models import TimeStampedModel
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.journal import choices


class Journal(TimeStampedModel):
    name = models.CharField(_('Note header'), max_length=255, null=True, blank=True)
    category = models.CharField(_('Category slug'), max_length=255, null=True, blank=True)
    content = models.TextField(_('Content'))
    user = models.ForeignKey('accounts.User', verbose_name=_('Creator'), on_delete=models.CASCADE, null=True)
    file = models.ForeignKey('patients.File', verbose_name=_('File'), on_delete=models.CASCADE, null=True)
    type = models.CharField(_('Note type'), choices=choices.JOURNAL_COMMENT_TYPE, max_length=10, default='comment')
    tag = models.CharField(_('Note tag'), choices=choices.JOURNAL_TAG_TYPE, max_length=10, blank=True, null=True)
    action = models.CharField(_('User Action'), choices=choices.ACTIONS, max_length=10, null=True)

    class Meta:
        verbose_name = _('Journal')
        verbose_name_plural = _('Journal')
        db_table = 'journal'
        ordering = ('-created',)

    def __str__(self):
        return self.name or self.content


class JournalComments(Journal):
    class Meta:
        proxy = True


class JournalEvents(Journal):
    class Meta:
        proxy = True
