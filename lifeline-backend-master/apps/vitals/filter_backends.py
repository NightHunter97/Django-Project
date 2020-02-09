import coreapi
from django.core.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend
from datetime import datetime


class VitalsFilterBackend(BaseFilterBackend):
    filtered_methods = ('GET', )

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='type', location='query', required=False, type='string', description='Filter by vital type'
            ),
            coreapi.Field(
                name='file', location='query', required=False, type='string', description='Filter by patient file'
            ),
            coreapi.Field(
                name='from', location='query', required=False, type='string', description='From date'
            ),
            coreapi.Field(
                name='to', location='query', required=False, type='string', description='To date'
            )
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        if request.method in self.filtered_methods:
            queryset = [
                item for item in queryset
                if item.type == request.query_params.get('type')
                and item.file.file_id == request.query_params.get('file')
            ]
            try:
                from_date = request.query_params.get('from')
                to = request.query_params.get('to')
                if from_date:
                    queryset = [item for item in queryset
                                if item.created.date() >= datetime.strptime(from_date, '%Y-%m-%d').date()]
                if to:
                    queryset = [item for item in queryset
                                if item.created.date() <= datetime.strptime(to, '%Y-%m-%d').date()]
            except (ValidationError, ValueError):
                return []
        return queryset
