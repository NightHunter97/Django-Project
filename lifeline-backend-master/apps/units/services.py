import datetime

from apps.units.models import Unit


def get_all_units():
    return Unit.objects.all()


def get_all_user_units(user):
    return Unit.objects.filter(user=user)


def get_unit(unit_id):
    return Unit.objects.filter(id=unit_id).first()


def get_unit_by_name(unit_name):
    return Unit.objects.filter(name__iexact=unit_name).first()


def get_new_patients_count(qs, date):
    return len([file for file in qs if file.created and file.created.date() == date.date()])


def get_patients_count(qs, date, field):
    return len([file for file in qs if getattr(file, field) and getattr(file, field) == date.date()])


def get_unit_patients(qs, iterations, prev_date, step=1, hourly=None):
    result = []
    new = released = temporary = 0
    for point in range(1, iterations+1):
        new += get_new_patients_count(qs, prev_date)
        temporary += get_patients_count(qs, prev_date, 'temporary_released_start')
        released += get_patients_count(qs, prev_date, 'closed_since')
        if point % step == 0:
            result.append({
                'date': prev_date,
                'new': new,
                'released': released,
                'temporary': temporary
            })
            new = released = temporary = 0
        prev_date += datetime.timedelta(**{'hours': 4} if hourly else {'days': 1})
    return result


def create_unit(name):
    return Unit.objects.create(name=name)
