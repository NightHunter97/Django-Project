import coreapi
from rest_framework.filters import BaseFilterBackend

from apps.patients.services import get_all_files
from apps.units.services import get_all_user_units


class UnitFilterBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='unit', location='query', required=True, type='string', description='Filter by unit')
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        unit_id = request.query_params.get('unit')
        if not unit_id or not unit_id.isdigit() or \
                int(unit_id) not in [unit.id for unit in get_all_user_units(request.user)]:
            unit = get_all_user_units(request.user).first()
            if not unit:
                return get_all_files().none(), 0
            unit_id = get_all_user_units(request.user).first().id
        return get_all_files().filter(unit=unit_id), unit_id
