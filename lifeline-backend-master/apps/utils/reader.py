from openpyxl import load_workbook
from django.utils.translation import ugettext_lazy as _


class XslxBaseReader:
    content_error = _('Wrong format')
    no_data_error = _('No data was parsed from file')

    header_fields_choices = ()

    def __init__(self, file):
        self._errors = []
        if file:
            self._wb = load_workbook(file)
        else:
            self._errors.append(_('File was not uploaded to server'))

    def get_error(self):
        return self._errors[0] if self._errors else None

    def _not_valid_header(self, row):
        for index, field in enumerate(self.header_fields_choices):
            if row[index].value and field[0] != row[index].value.lower().strip():
                return True
