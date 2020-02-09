import copy

from rest_framework import status

from apps.medications.models import Prescription, MedicationCategory, PrescriptionLog, MedicationIntake, Drug
from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response

from apps.tasks.date_periodic_parsers import parse_periodic_data
from apps.tasks.services import tasks_root_update

def get_all_drugs():
    return Drug.objects.all()

def get_all_intakes():
    return MedicationIntake.objects.all()

def get_all_prescriptions():
    return Prescription.objects.all()


def get_all_prescriptions_by_file(file):
    return Prescription.objects.filter(file=file)


def get_all_logs():
    return PrescriptionLog.objects.all()


def get_all_medications():
    return MedicationCategory.objects.all()


def create_prescription_log(prescription, data):
    fields_map = {
        'max_quantity': 'Maximum posology per day',
        'category': 'Medicine',
    }
    local = copy.copy(data)
    actions = []
    history = local.pop('is_active', None)
    comment = local.pop('comment', None)
    if history is False and history != prescription.is_active:
        actions.append(str(_('Moved to History')))
    if comment and comment != prescription.comment:
        actions.append(str(_('Comment was changed')))
    for field, value in local.items():
        prescription_value = getattr(prescription, field)
        if prescription_value != value:
            actions.append(
                f'set {fields_map.get(field, field).title()} from {prescription_value} to {value or "Empty"}'
            )
    if actions:
        actions.reverse()
        return PrescriptionLog.objects.create(
            prescription=prescription, editor=prescription.editor, comment=prescription.comment,
            actions=', '.join(actions)
        )


def create_tasks_for_medications(request, data):
    from apps.medications.serializers import PrescriptionScheduleSerializer

    data = parse_periodic_data(data, file=data.get('file'), user=request.user)
    if len(data) > 300:
        return Response({'repeatMode': [_("Repeats can't be more than 300.")]}, status=status.HTTP_400_BAD_REQUEST)
    serializer = PrescriptionScheduleSerializer(data=data, many=True)
    serializer.is_valid(raise_exception=True)
    tasks = serializer.save()
    tasks_root_update(request.data, tasks)
