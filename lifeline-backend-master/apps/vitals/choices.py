from django.utils.translation import ugettext_lazy as _

VITALS = ['pressure', 'pulse', 'height', 'temp', 'sugar', 'weight', 'saturation', 'breath']

VITAL_TYPES = (
    ('pressure', _('Blood pressure')),
    ('pulse', _('Pulse')),
    ('height', _('Height')),
    ('temp', _('Temperature')),
    ('sugar', _('Blood sugar')),
    ('weight', _('Weight')),
    ('saturation', _('O2 saturation')),
    ('breath', _('Breathing rate')),
)

VITAL_TYPES_SLUGS_MAP = {
    'pressure': 'blood-pressure',
    'pulse': 'pulse',
    'height': 'height',
    'temp': 'temperature',
    'sugar': 'blood-sugar',
    'weight': 'weight',
    'saturation': 'o2-saturation',
    'breath': 'breathing-rate',
}

VITAL_UNITS_MAPPING = {
    'pressure': _('mmHG'),
    'pulse': _('bpm'),
    'height': _('cm'),
    'temp': _('c°'),
    'sugar': _('mg/dL'),
    'weight': _('kg'),
    'saturation': _('%'),
    'breath': _('cycle/min')
}
