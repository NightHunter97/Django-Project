from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _

class MedicationCategory(models.Model):
    term = models.CharField(_('Category'), max_length=255)

    class Meta:
        verbose_name = _('Medication Category')
        verbose_name_plural = _('Medication Categories')
        db_table = 'medication_categories'
        ordering = ('term',)

    def __str__(self):
        return self.term


class Prescription(TimeStampedModel):
    user = models.ForeignKey('accounts.User', verbose_name=_(
        'Creator'), on_delete=models.CASCADE, null=True)
    drug = models.ForeignKey('Drug', verbose_name=_(
        'Drug'), on_delete=models.CASCADE, null=True, blank=True)
    file = models.ForeignKey(
        'patients.File', verbose_name=_('File'), on_delete=models.CASCADE, null=True, blank=True
    )

    task_type = _('Medication')

    MODE_DAILY = 'DAILY'
    MODE_CONDITIONAL = 'CONDITIONAL'
    RECCURENCE_DAYS = 'DAYS'
    RECCURENCE_WEEKS = 'WEEKS'
    RECCURENCE_MONTHS = 'MONTHS'
    MEAL_BEFORE = 'BEFORE'
    MEAL_AFTER = 'AFTER'
    DURATION_INDEFINITE = 'INDEF'
    DURATION_FIXED = 'FIXED'

    MODE_VALUES = (
        (MODE_DAILY, _('Daily')),
        (MODE_CONDITIONAL, _('Conditional')),
    )
    RECCURENCE_VALUES = (
        (RECCURENCE_DAYS, _('Days')),
        (RECCURENCE_WEEKS, _('Weeks')),
        (RECCURENCE_MONTHS, _('Months')),
    )
    DURATION_VALUES = (
        (DURATION_INDEFINITE, _('Indefinite')),
        (DURATION_FIXED, _('Fixed')),
    )
    MEAL_VALUES = (
        (MEAL_BEFORE, _('Before')),
        (MEAL_AFTER, _('After')),
    )
    PRESCRIPTION_TYPE_CHOICES = (
        ('time-slots', _('Time slots')),
        ('fixed-times', _('Fixed times')),
        ('fixed-times-dow', _('Fixed times by day of week')),
        ('one-shot', _('One shot')),
        ('conditional', _('Conditional'))
    )

    mode = models.CharField('type', max_length=11,
                            choices=MODE_VALUES, null=True, blank=True)
    meal = models.CharField(_('Meal'), max_length=6,
                            choices=MEAL_VALUES, null=True, blank=True)
    prescription_type = models.CharField(
        max_length=20, default='conditional', choices=PRESCRIPTION_TYPE_CHOICES)
    duration = models.CharField(_('Duration'), max_length=5, choices=DURATION_VALUES,
                                default=DURATION_INDEFINITE, null=True, blank=True)

    creator = models.CharField(_('Creator'), max_length=255)
    editor = models.CharField(
        _('Editor'), max_length=255, null=True, blank=True)
    comment = models.TextField(_('Comment'), null=True, blank=True, default='')
    max_quantity = models.CharField(
        _('Maximum posology per day (Co/day)'), max_length=255, null=True, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)

    duration_start = models.DateTimeField(
        _('Duration start'), null=True, blank=True)
    duration_end = models.DateTimeField(
        _('Duration end'), null=True, blank=True)

    # Repeat (True/False), ie. every 3 days
    repeat = models.BooleanField(_('Repeat'), default=False)
    repeat_every = models.IntegerField(_('Every'), null=True, blank=True)
    repeat_reccurence = models.CharField(
        _('Reccurence'), max_length=6, choices=RECCURENCE_VALUES, null=True, blank=True)

    # Cycle (True/False), ie every N days over N weeks
    cycle = models.BooleanField(_('Cycle'), default=False)
    cycle_every_value = models.IntegerField(_('Every'), null=True, blank=True)
    cycle_every_reccurence = models.CharField(
        _('Reccurence'), max_length=6, choices=RECCURENCE_VALUES, null=True, blank=True)
    cycle_over_value = models.IntegerField(_('Value'), null=True, blank=True)
    cycle_over_reccurence = models.CharField(
        _('Reccurence'), max_length=6, choices=RECCURENCE_VALUES, null=True, blank=True)

    class Meta:
        verbose_name = _('Prescription')
        verbose_name_plural = _('Prescriptions')
        db_table = 'prescriptions'
        ordering = ('-created',)

    def __str__(self):
        if self.drug:
            title = self.drug.category.term
        else:
            title = 'N/A'
        return f'{title}'


class TimeSlot(models.Model):
    prescription = models.ForeignKey(
        'Prescription',
        related_name='time_slots',
        verbose_name=_('Prescription'),
        on_delete=models.CASCADE
    )

    TIME_SLOT_TYPE_CHOICES = (
        ('step', _('Step')),
        ('step-dow', _('Step with day of week')),
        ('one-shot', _('One shot'))
    )

    DOW_VALUES = (
        ('mon', _('Monday')),
        ('tue', _('Tuesday')),
        ('wed', _('Wednesday')),
        ('thu', _('Thursday')),
        ('fri', _('Friday')),
        ('sat', _('Saturday')),
        ('sun', _('Sunday')),
    )

    dow = models.CharField(_('Day of week'), max_length=3,
                           choices=DOW_VALUES, null=True, blank=True)
    time_slot_type = models.CharField(_('Type'), max_length=10,
                                      choices=TIME_SLOT_TYPE_CHOICES)

    quantity = models.FloatField(_('Quantity'))
    time_step = models.IntegerField(_('MS from start of day'), null=True, blank=True)
    datetime = models.DateTimeField(_('Date time of intake'), null=True, blank=True)

    class Meta:
        verbose_name = _('TimeSlot')
        verbose_name_plural = _('TimeSlots')
        db_table = 'time_slots'


class Drug(TimeStampedModel):
    name = models.CharField(_('Name'), max_length=255)
    category = models.ForeignKey(
        'MedicationCategory',
        verbose_name=_('Drug'),
        related_name='drugs',
        on_delete=models.CASCADE
    )
    code = models.CharField(_('Code'), max_length=64, default='code')
    vmp_code = models.CharField(
        _('VMP Code'), max_length=16, null=True, blank=True)
    unit = models.CharField(_('Unit'), max_length=128)

    def __str__(self):
        return f'{self.name}'

class MedicationIntake(TimeStampedModel):
    prescription = models.ForeignKey('Prescription', related_name='intakes', verbose_name=_(
        'Prescription'), on_delete=models.CASCADE)
    comment = models.TextField(_('Comment'), null=True, blank=True)

    time = models.DateTimeField(_('Start of medication intake time'))

    ACTION_TYPE_D = 'D'
    ACTION_TYPE_DC = 'DC'
    ACTION_TYPE_ND = 'ND'

    ACTION_TYPE_CHOICES = (
        (ACTION_TYPE_D, 'Done'),
        (ACTION_TYPE_DC, 'Done + comment'),
        (ACTION_TYPE_DC, 'Not done')
    )

    action_type = models.CharField(
        max_length=100,
        choices=ACTION_TYPE_CHOICES
    )

    STOCK_TYPE_PATIENT = 'patient'

    STOCK_TYPE_CHOICES = (
        (STOCK_TYPE_PATIENT, 'Patient stock type'),
    )

    stock_type = models.CharField(
        max_length=100,
        choices=STOCK_TYPE_CHOICES,
        default=STOCK_TYPE_PATIENT
    )
    quantity = models.FloatField(_('Quantity'))

    class Meta:
        verbose_name = _('Medication intake')
        verbose_name_plural = _('Medication intakes')
        db_table = 'medication_intakes'
        ordering = ('-created',)


class PrescriptionLog(TimeStampedModel):
    prescription = models.ForeignKey('Prescription', verbose_name=_(
        'Prescription'), on_delete=models.CASCADE)
    editor = models.CharField(
        _('Editor'), max_length=255, null=True, blank=True)
    comment = models.TextField(_('Comment'), null=True, blank=True)
    actions = models.TextField(_('Actions'), null=True, blank=True)
    user = models.ForeignKey('accounts.User', verbose_name=_(
        'Creator'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('Prescription Log')
        verbose_name_plural = _('Prescription Logs')
        db_table = 'prescription_logs'
        ordering = ('-created',)

    def __str__(self):
        return self.comment or f'Prescription Log {self.pk}'


class MedicationTherapy(Prescription):
    class Meta:
        proxy = True


class MedicationHistory(Prescription):
    class Meta:
        proxy = True
