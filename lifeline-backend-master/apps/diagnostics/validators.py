import os
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def file_extension_validator(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.xlsx', '.xls']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_('Only .xlsx and .xls are accepted'))
