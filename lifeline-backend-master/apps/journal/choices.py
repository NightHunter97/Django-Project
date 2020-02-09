from django.utils.translation import ugettext_lazy as _


JOURNAL_COMMENT_TYPE = (
    ('comment', _('Comment')),
    ('event', _('Event'))
)

JOURNAL_TAG_TYPE = (
    ('medical', _('Medical info')),
    ('nursing', _('Nursing info')),
    ('caregiver', _('Caregiver info')),
    ('psycho', _('Psychotherapy')),
    ('physio', _('Physiotherapy')),
    ('social', _('Social info')),
    ('staff', _('Staff meeting')),
    ('night', _('Nightshift')),
    ('fall', _('Fall')),
    ('confusion', _('Confusion')),
    ('disorient', _('Disorientation')),
    ('run', _('Runaway')),
    ('behavior', _('Behavior disorder')),
    ('agressive', _('Agressiveness')),
    ('agitate', _('Agitation')),
    ('drug', _('Drug use'))
)

ACTIONS = (
    ('create', _('Created')),
    ('add', _('Added')),
    ('edit', _('Edited')),
    ('delete', _('Deleted')),
    ('status', _('Status changed')),
    ('cured', _('Cured'))
)
