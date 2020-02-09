import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from autoslug import AutoSlugField

from apps.tasks import choices
from lifeline.storage_backends import PublicStaticStorage


class Category(models.Model):
    name = models.CharField(_('Category'), max_length=255)
    slug = AutoSlugField(populate_from='name', null=True, unique=True)
    icon = models.CharField(_('Static Icon'), max_length=255, choices=choices.STATIC_ICONS, null=True, blank=True)
    image = models.ImageField(_('Dynamic Icon'), null=True, blank=True, storage=PublicStaticStorage())
    groups = models.ManyToManyField(
        'auth.Group', verbose_name=_('Groups'), related_name="categories", blank=True
    )

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        db_table = 'category'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(_('Task'), max_length=255)
    category = models.ForeignKey(
        'Category', verbose_name=_('Category'), related_name='tasks', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        db_table = 'task'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Schedule(models.Model):
    task = models.ForeignKey(
        'Task', verbose_name=_('Task'), related_name="schedules", on_delete=models.CASCADE, null=True, blank=True
    )
    file = models.ForeignKey(
        'patients.File', verbose_name=_('File'), related_name="schedules", on_delete=models.CASCADE, null=True, blank=True
    )
    date = models.DateField(_('Task Date'), auto_now=False, auto_now_add=False)
    time = models.TimeField(_('Task Time'), null=True, default='12:00')
    members = models.ManyToManyField(
        'accounts.User', verbose_name=_('Team Members'), related_name="schedules", blank=True
    )
    comment = models.TextField(_('Comment'), null=True, blank=True)
    status = models.CharField(_('Task Status'), max_length=4, choices=choices.TASK_STATUSES, null=True, blank=True)
    root_id = models.IntegerField(null=True, blank=True)
    periodic = models.CharField(_('Task periodic'), choices=choices.REPEAT, max_length=5, null=True, blank=True)
    slot = models.BooleanField(_('Is time slot'), default=False)
    wound = models.ForeignKey(
        'wounds.Wound', verbose_name=_('Wound'), on_delete=models.CASCADE, null=True, blank=True
    )
    prescription = models.ForeignKey(
        'medications.Prescription', verbose_name=_('Prescription'), on_delete=models.CASCADE, null=True, blank=True
    )
    creator = models.ForeignKey('accounts.User', verbose_name=_('Creator'), on_delete=models.CASCADE, null=True)

    @property
    def is_expired(self):
        return self.status == 'STOP'

    @property
    def get_time_slot(self):
        if self.slot:
            return self.format_time(self.time) + ' - ' + self.format_time(self.get_slot_end(self.time))

    @staticmethod
    def get_slot_end(slot_time):
        return (datetime.datetime.combine(datetime.date(1, 1, 1), slot_time) + datetime.timedelta(hours=2)).time()

    @staticmethod
    def format_time(time):
        return f'{time.strftime("%I:00 %p").replace("PM", "p.m.").replace("AM", "a.m.")}'

    class Meta:
        verbose_name = _('Schedule')
        verbose_name_plural = _('Schedules')
        db_table = 'schedules'
        ordering = ('date',)

    def __str__(self):
        return str(self.date)


class RepeatedTask(models.Model):
    root_id = models.IntegerField(primary_key=True, unique=True)
    date = models.DateField(auto_now=False, auto_now_add=False)
    time = models.TimeField(null=True, default='12:00')
    comment = models.TextField(null=True, blank=True)
    periodic = models.CharField(max_length=5, null=True, blank=True)
    slot = models.BooleanField(default=False)
    times = models.CharField(max_length=255, null=True, blank=True)
    interval = models.IntegerField(blank=True, null=True)
    week_days = models.CharField(max_length=64, null=True, blank=True)
    end_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    repeats = models.IntegerField(blank=True, null=True)
    members = models.ManyToManyField('accounts.User', blank=True)

    class Meta:
        verbose_name = _('RepeatedTask')
        verbose_name_plural = _('RepeatedTasks')
        db_table = 'repeatedtasks'
        ordering = ('root_id',)

    def __str__(self):
        return str(self.root_id)
