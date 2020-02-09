import coreapi
from rest_framework.filters import BaseFilterBackend


class FileJournalFilter(BaseFilterBackend):
    filter_field_mapping = {
        'date': 'created__date',
        'file': 'file__file_id',
        'type': 'type',
        'tag': 'tag',
    }

    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='file', location='query', type='string', description='Filter by file id'),
            coreapi.Field(
                name='date', location='query', type='date', description='Filter by date. Example: 2000-01-01'
                          ),
            coreapi.Field(
                name='type', location='query', type='string', description='Filter by type Example: comment, event'
            ),
            coreapi.Field(
                name='tag', location='query', type='string',
                description='Filter by tag (Check tag types in META endpoint)'
            )

        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        filters = {}
        for key, val in self.filter_field_mapping.items():
            _filter = request.query_params.get(key)
            if _filter:
                filters.update({val: _filter})

        return queryset.filter(**filters)
