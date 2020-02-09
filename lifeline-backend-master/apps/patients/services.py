from collections import OrderedDict

from django.db.models import Q

from apps.patients.models import Patient, File, ArchiveComment, EmergencyContact


def get_all_patients():
    return Patient.objects.all()


def get_patient_by_pk(pk):
    return Patient.objects.filter(pk=pk).first()


def get_none_files():
    return File.objects.none()


def get_released_patients():
    return Patient.objects.exclude(files__in=File.objects.filter(closed_since__isnull=True))


def get_patient(patient_id):
    return Patient.objects.filter(patient_id=patient_id).first()


def get_patient_by_nr(national_register):
    return Patient.objects.filter(national_register=national_register).first()


def get_all_archive_comments():
    return ArchiveComment.objects.all()


def get_active_patient_file(patient):
    file = File.objects.filter(patient=patient).first()
    if file and not file.is_released:
        return file


def get_last_closed_patient_file(patient):
    try:
        file = File.objects.filter(patient=patient, closed_since__isnull=False).latest("closed_since")
    except File.DoesNotExist:
        file = None
    if file and file.is_released:
        return file


def create_file_for_patient(patient, unit):
    return File.objects.create(patient=patient, unit_id=unit)


def update_file_unit(file, unit):
    return File.objects.filter(file_id=file).update(unit_id=unit)


def get_all_files():
    return File.objects.select_related('unit', 'patient').all()


def get_admission_files():
    return File.objects.select_related('patient').all().order_by('-created')


def get_archived_files():
    return File.objects.filter(closed_since__isnull=False).select_related('patient').all().order_by('-closed_since')


def get_all_files_in_unit(unit):
    return File.objects.filter(unit=unit).values_list('file_id', flat=True)


def get_all_files_in_units(unit_list):
    return [file for file in File.objects.filter(unit__in=unit_list).distinct() if not file.is_released]


def get_id_by_file_id(file_id):
    file = File.objects.filter(file_id=file_id).first()
    if not file:
        return File.objects.none()
    return file.id


def get_file_by_file_id(file_id):
    return File.objects.filter(file_id=file_id).first()


def get_file_by_pk(pk):
    return File.objects.get(pk=pk)


def does_email_exist(email, current, pk):
    if email:
        return Patient.objects.filter(email=email).exclude(Q(patient_id=current) | Q(id=pk)).exists()


def does_file_exist(file):
    return File.objects.filter(file_id=file).exists()


def already_has_file(patient):
    return File.objects.filter(patient=patient, closed_since__isnull=True).exists()


def get_all_emergency_contacts():
    return EmergencyContact.objects.all()


def get_all_patient_file_ids(patient_id):
    patient = Patient.objects.filter(pk=patient_id).first()
    if patient:
        return patient.files.all().values_list('file_id', flat=True)


def get_active_emergency_contacts():
    return EmergencyContact.objects.filter(deleted=False)


def get_patients_for_export(patient_id):
    patient = Patient.objects.filter(pk=patient_id).prefetch_related(
        'files',
        'emergencycontact_set',
        'files__diagnostic_set',
        'files__diagnostic_set__diagnose',
        'files__diagnostic_set__screening',
        'files__schedules',
        'files__schedules__task',
        'files__schedules__members',
        'files__schedules__creator',
        'files__evaluation_set',
        'files__journal_set__user',
        'files__report_set',
        'files__vitalsparam_set',
        'files__wound_set',
        'files__prescription_set__schedule_set',
        'files__prescription_set__schedule_set__creator',
        'files__prescription_set__category',
        'files__evaluation_set'
    ).first()
    return patient


def vitals_to_table(files):

    def new_row():
        return OrderedDict(
            [
                ('time', None),
                ('pressure', None),
                ('pulse', None),
                ('height', None),
                ('temp', None),
                ('sugar', None),
                ('weight', None),
                ('saturation', None),
                ('breath', None)
            ]
        )

    result = {}
    for file in files:
        list_vitals = []
        row_vitals = new_row()
        for vital in file.vitalsparam_set.all():
            if not row_vitals.get('time'):
                row_vitals['time'] = vital.created.strftime("%b %d %Y %H:%M")
                row_vitals[vital.type] = vital.value

            elif vital.created.strftime("%b %d %Y %H:%M") == row_vitals['time']:
                row_vitals[vital.type] = vital.value
            else:
                list_vitals.append(row_vitals)

                row_vitals = new_row()
                row_vitals['time'] = vital.created.strftime("%b %d %Y %H:%M")
                row_vitals[vital.type] = vital.value

        list_vitals.append(row_vitals)
        result.update({file.file_id: list_vitals})
    return result
