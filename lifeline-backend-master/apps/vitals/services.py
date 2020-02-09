from apps.vitals.choices import VITALS, VITAL_TYPES
from apps.vitals.models import VitalsParam


def get_all_vitals():
    return VitalsParam.objects.all()


def get_vitals_by_file(file_id):
    return VitalsParam.objects.filter(file__file_id=file_id)


def get_last_vitals_by_file(file_id, params=None):
    vitals = get_vitals_by_file(file_id)
    data = {}
    for param in params or VITALS:
        vital = vitals.filter(type=param).first()
        if vital:
            if not params:
                data.update({dict(VITAL_TYPES).get(param): vital.value})
            else:
                data.update({param: vital.value})
    return data
