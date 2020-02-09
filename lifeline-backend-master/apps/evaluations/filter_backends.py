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
        return queryset


class TypeFilterBackend(BaseFilterBackend):

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='survey_type', location='query', required=True, type='string', description='Filter by survey type'
            ),
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        search = request.query_params.get('survey_type')
        if not search:
            return queryset
        return queryset.filter(name=search).order_by('-created')


class SurveyTypesFilterBackend(BaseFilterBackend):

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='archive', location='query', required=False, type='string', description='Filter by archive'
            ),
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        search = request.query_params.get('archive')

        queryset = queryset.filter(is_active=(not bool(search))).order_by('name')

        return queryset
