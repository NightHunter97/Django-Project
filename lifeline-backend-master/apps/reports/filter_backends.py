import coreapi
from rest_framework.filters import BaseFilterBackend


class FileFilterBackend(BaseFilterBackend):

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='file', location='query', required=False, type='string', description='Filter by patient file'
            ),
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        file = request.query_params.get('file')
        if file:
            return queryset.filter(file__file_id=file)
        return queryset.none()
