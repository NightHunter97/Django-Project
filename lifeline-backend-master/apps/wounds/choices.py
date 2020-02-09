from django.utils.translation import ugettext_lazy as _

WOUND_TYPES = (
    ('OPEN', _('Open wound')),
    ('SUTU', _('Sutured wound')),
    ('SORE', _('Decubitus ulcer/pressure sore')),
    ('TRAU', _('Traumatic wound')),
    ('SKIN', _('Skin graft wound')),
    ('OPER', _('Post-operative wound')),
    ('DRAI', _('Post-drainage wound')),
    ('BURN', _('Burn')),
    ('ABSC', _('Abscess')),
    ('ULCR', _('Ulcer')),
    ('PERI', _('Periphlebitis')),
    ('LESI', _('Skin lesion')),
    ('FIST', _('Arteriovenous fistula')),
    ('SPRA', _('Sprain')),
    ('CONT', _('Contusion')),
    ('HAEM', _('Haematoma'))
)

LOCALIZATION = (
    ('HEAD', _('Head')),
    ('NECK', _('Neck')),
    ('THOR', _('Thorax')),
    ('UABD', _('Upper abdomen')),
    ('LABD', _('Lower abdomen')),
    ('UBCK', _('Upper back')),
    ('LBCK', _('Lower back')),
    ('SHDR', _('Shoulder')),
    ('ARM', _('Arm')),
    ('FORE', _('Forearm')),
    ('WRST', _('Wrist')),
    ('HAND', _('Hand')),
    ('GENI', _('Genital area')),
    ('BUTT', _('Buttock crease')),
    ('ING', _('Inguinal folds')),
    ('THGH', _('Thigh')),
    ('LEG', _('Leg')),
    ('FOOT', _('Foot'))
)
