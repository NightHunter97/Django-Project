import uuid

from django.http import Http404
from django.contrib.admin.models import LogEntry
from django.core.cache import cache

from apps.accounts.models import User, Activity
from apps.patients.services import get_patient_by_pk


def get_all_users():
    return User.objects.all()


def get_active_users():
    return User.objects.filter(is_active=True)


def get_all_users_in_unit(unit_id):
    return User.objects.filter(units=unit_id)


def get_user_by_uuid(user_uuid):
    try:
        return User.objects.filter(uuid=uuid.UUID(user_uuid)).first()
    except (ValueError, TypeError):
        raise Http404


def get_log_entry_actions(uuid, patient, start, end):
    qs = LogEntry.objects.filter(user=uuid)
    if start:
        qs = qs.filter(action_time__date__gte=start)
    if end:
        qs = qs.filter(action_time__date__lte=end)
    if patient:
        qs = qs.filter(adminactivity__patient_id=patient)
    return qs


def get_user_activity(email, patient_pk, start, end):
    qs = Activity.objects.filter(email=email)
    patient = get_patient_by_pk(patient_pk)
    if patient:
        qs = qs.filter(patient_id=patient.patient_id)
    if start:
        qs = qs.filter(created__date__gte=start)
    if end:
        qs = qs.filter(created__date__lte=end)
    return qs


def clear_brusafe_token(user):
    cache.delete(f'{user.uuid}_brusafe')
