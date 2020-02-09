from django.utils.translation import ugettext_lazy as _

from apps.medications.models import MedicationCategory
from apps.medications.tasks import medication_bulk_create, medication_update


class CSVReader:
    fields = ('Code', 'VmpCode', 'OfficialName', 'UnitLabel_En', 'UnitLabel_Fr', 'UnitLabel_Nl')
    error = None

    def __init__(self, file):
        self.file = file

    def proceed(self):
        fields_mapping = {
            'Code': 0,
            'VmpCode': 0,
            'OfficialName': 0,
            'UnitLabel_En': 0,
            'UnitLabel_Fr': 0,
            'UnitLabel_Nl': 0,
        }
        lines = self.file.readlines()
        if not lines:
            self.error = _('Empty file')
            return
        headers = lines[0].decode('latin_1').rstrip().split(';')
        for field in self.fields:
            if field not in headers:
                self.error = _('Wrong content')
                return
            fields_mapping[field] = headers.index(field)
        medications = []
        self._bulk_medication_create(fields_mapping, lines, medications)

    @classmethod
    def _bulk_medication_create(cls, fields_mapping, lines, medications):
        codes = MedicationCategory.objects.all().values_list('code', flat=True)
        update_medications = []
        for line in lines[1:]:
            values = line.decode('utf-8').rstrip().split(';')
            unit_en = values[fields_mapping['UnitLabel_En']]
            unit_fr = values[fields_mapping['UnitLabel_Fr']]
            unit_nl = values[fields_mapping['UnitLabel_Nl']]
            medication_data = dict(
                code=values[fields_mapping['Code']],
                vmp_code=values[fields_mapping['VmpCode']],
                term=values[fields_mapping['OfficialName']],
                unit_en=unit_en,
                unit_fr=unit_fr,
                unit_nl=unit_nl
            )
            if values[fields_mapping['Code']] in codes:
                update_medications.append(medication_data)
            else:
                medications.append(medication_data)
        medication_bulk_create.delay(medications)
        medication_update.delay(update_medications)
