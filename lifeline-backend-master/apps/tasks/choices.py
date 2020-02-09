from django.utils.translation import ugettext_lazy as _


TASK_STATUSES = (
    ('DONE', _('Done')),
    ('DISP', _('Displaced')),
    ('UNDN', _('Undone')),
    ('STOP', _('Stop')),
    ('SUSP', _('Suspend')),
)

REPEAT = (
    ('DAY', _('Daily')),
    ('WEEK', _('Weekly')),
    ('MONTH', _('Monthly')),
    ('YEAR', _('Yearly')),
)

STATIC_ICONS = (
    ('tasks/icons/accompaniment-appointments-and-procedures.svg', 'Accompaniment, Appointments and Procedures'),
    ('tasks/icons/assessment-and-protection.svg', _('Assessment and Protection')),
    ('tasks/icons/basic-nursing-care.svg', _('Basic nursing care')),
    ('tasks/icons/physio-treatment.svg', _('Physio Treatment')),
    ('tasks/icons/psychol-care.svg', _('Psycho care')),
    ('tasks/icons/relational-treatment-and-care.svg', _('Relational treatment and care')),
    ('tasks/icons/sa-monitoring.svg', _('SA monitoring')),
    ('tasks/icons/sample.svg', _('Sample')),
    ('tasks/icons/technical-act.svg', _('Technical act')),
    ('tasks/icons/therapeutic-activity.svg', _('Therapeutic activity')),
    ('tasks/icons/therapeutic-education.svg', _('Therapeutic education')),
    ('tasks/icons/medication.svg', _('Medication')),
)
