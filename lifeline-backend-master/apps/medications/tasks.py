from apps.medications.models import MedicationCategory
from lifeline.celery import app


@app.task
def medication_bulk_create(medications):
    MedicationCategory.objects.bulk_create([MedicationCategory(
        code=medication['code'],
        vmp_code=medication['vmp_code'],
        term=medication['term'],
        unit_en=medication['unit_en'],
        unit_fr=medication['unit_fr'],
        unit_nl=medication['unit_nl']) for medication in medications]
    )


@app.task
def medication_update(medications):
    for medication in medications:
        category = MedicationCategory.objects.get(code=medication['code'])
        category.vmp_code = medication['vmp_code']
        category.term = medication['term']
        category.unit_en = medication['unit_en']
        category.unit_fr = medication['unit_fr']
        category.unit_nl = medication['unit_nl']
        category.save()
