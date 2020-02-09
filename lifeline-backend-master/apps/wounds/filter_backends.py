import coreapi
from rest_framework.filters import BaseFilterBackend

from apps.wounds.services import get_filtered_wounds, get_all_wounds, get_empty_wounds


class IsCuredBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='cured', location='query', required=False, type='boolean',
                          description='Filter by active/inactive wounds'),
            coreapi.Field(
                name='file', location='query', required=False, type='string', description='Filter by patient file'
            )
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        is_cured = request.query_params.get('cured')
        file = request.query_params.get('file')
        if not file:
            return get_empty_wounds()
        if is_cured == 'true':
            return get_filtered_wounds(True, file)
        if is_cured == 'false':
            return get_filtered_wounds(False, file)
        return get_all_wounds().filter(file__file_id=file)


class WoundEvolutionsBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='wound', location='query', required=False, type='string', description='Filter wound id'),
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        return queryset
