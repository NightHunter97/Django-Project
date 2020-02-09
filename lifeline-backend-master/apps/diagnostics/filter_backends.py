import coreapi
from rest_framework.filters import BaseFilterBackend


class DiagnosticTypeFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='type', location='query', type='string',
                          description='Filter by diagnostic type. Eg. diagnose, screening, anamnesis'),
            coreapi.Field(name='file', location='query', type='string', description='Filter by file id')
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        return queryset
