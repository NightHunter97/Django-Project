import coreapi
from rest_framework.filters import BaseFilterBackend


class IsActivePrescriptionBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='active', location='query', required=False, type='boolean', description='Is active prescription'),
            coreapi.Field(name='file', location='query', required=False, type='string', description='Filter by file'),
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        return queryset


class PrescriptionLogsBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='prescription', location='query', required=True, type='string', description='Filter by prescription id'),
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        prescription = request.query_params.get('prescription')
        if not prescription:
            return queryset.none()
        return queryset.filter(prescription=prescription)


class MedicationIntakesBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='patient_id', location='query', required=True,
                          type='string', description='Patient id'),
            coreapi.Field(name='start_of_ts', location='query', required=True,
                          type='string', description='Start of time period timestamp'),
            coreapi.Field(name='end_of_ts', location='query', required=True,
                          type='string', description='End of time period timestamp'),
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        # @TODO should construct queryset depends on following parameters:
        # patient_id = int(request.query_params.get('patient_id'))
        # start_of_ts = int(request.query_params.get('start_of_ts'))
        # end_of_ts = int(request.query_params.get('end_of_ts'))

        return queryset
