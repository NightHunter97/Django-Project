from apps.wounds.models import Wound, Evolution


def get_all_wounds():
    return Wound.objects.prefetch_related('evolution_set').all()


def get_wound(wound):
    return Wound.objects.filter(pk=wound).first()


def get_empty_wounds():
    return Wound.objects.none()


def get_empty_evolutions():
    return Evolution.objects.none()


def get_all_evolutions():
    return Evolution.objects.all()


def get_wound_evolutions(wound):
    ids = list(Evolution.objects.filter(wound=wound).values_list('id', flat=True))
    return Evolution.objects.filter(id__in=ids[:-1]) if ids else Evolution.objects.none()


def get_filtered_wounds(is_cured, file):
    return Wound.objects.filter(is_cured=is_cured, file__file_id=file)


def delete_evolution_history(ids):
    count, _ = Evolution.objects.filter(id__in=ids).delete()
    return {'deleted': count}
