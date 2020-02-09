import coreapi
from rest_framework.filters import BaseFilterBackend

from apps.tasks.services import get_tasks_in_category, get_all_scheduled_tasks


class DateFilterBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='date', location='query', required=False, type='string', description='Filter by date'),
            coreapi.Field(name='file', location='query', required=False, type='string', description='Filter by file id')
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        return get_all_scheduled_tasks()


class TaskFilterBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='category', location='query', required=False, type='string',
                description='Filter tasks by specific category slug'
            )
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        category = request.query_params.get('category')
        if not category:
            return queryset
        return get_tasks_in_category(category)
