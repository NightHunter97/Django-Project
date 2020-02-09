import re
from datetime import datetime
from dateutil import parser

import coreapi
from django.db.models import Q
from django.utils import translation
from rest_framework.filters import BaseFilterBackend
from rest_framework import filters

from apps.patients.choices import TASKS_FILTER
from apps.patients.services import get_released_patients, get_all_files, get_none_files
from apps.tasks.services import get_open_tasks
from django.utils.translation import ugettext_lazy as _


class ActivePatientsBackend(filters.BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='active', location='query', type='boolean', description='Filter by active patients'),
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        is_active = request.query_params.get('active')
        if not is_active:
            return queryset
        if is_active == 'true':
            return [file for file in queryset if not file.is_released]
        return [file for file in queryset if file.is_released]


class SearchStatusPatientsBackend(filters.BaseFilterBackend):
    search_mapping = {
        'present': 'is_present',
        'temporary released': 'is_temporary',
    }

    def filter_queryset(self, request, queryset, *args, **kwargs):
        search = request.query_params.get('search')
        if not search:
            return queryset
        for criteria, field in self.search_mapping.items():
            if criteria.find(search.lower()) == 0:
                ids = [file.id for file in get_all_files().filter(unit__in=request.user.units.all())
                       if getattr(file, field)]
                queryset |= get_all_files().filter(id__in=ids)
        return queryset


class StepPatientSearchFilter(filters.BaseFilterBackend):
    search_result_limit = 50

    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='step', location='query', type='string',
                          description='Filter by patient step. Example: all, info, social, insurance'),
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        search = request.query_params.get('search', '').strip()
        if search:
            search = search.lower()
            results = get_released_patients().filter(full_name__icontains=search)[:self.search_result_limit]
            starts = [patient for patient in results if patient.full_name.lower().startswith(search)]
            rest = [patient for patient in results if not patient.full_name.lower().startswith(search)]
            return starts + rest
        return queryset


class FileFilterBackend(filters.BaseFilterBackend):

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='file', location='query', required=True, type='string', description='Filter by patient file'
            )
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        return queryset.filter(file__file_id=request.query_params.get('file'))


class OpenStatusSortingBackend(filters.BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='open_tasks', location='query', required=False, type='string',
                description='Filter by tasks(daily, my, due)'
            )
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        data = [file for file in queryset if not file.is_released]
        if 'open_tasks' in request.query_params.get('ordering', []):
            for row in queryset:
                row.open_tasks = get_open_tasks(row.file_id).count()
            data.sort(key=lambda x: x.open_tasks, reverse=True)
            return data
        if 'status' in request.query_params.get('ordering', []):
            def __get_status(obj):
                if obj.is_released:
                    return _('Released')
                if obj.is_temporary:
                    return _('Temporary released')
                return _('Present')

            for row in queryset:
                row.patient_status = __get_status(row)
            data.sort(key=lambda x: x.patient_status)
            return data
        return queryset


class TaskFilterBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='task', location='query', required=False, type='string',
                description='Filter by tasks(daily, my, due)'
            )
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        if request.query_params.get('task') == TASKS_FILTER[0][0]:
            return queryset.filter(
                schedules__status__isnull=True,
                schedules__date=datetime.today().date()
            ).distinct()
        if request.query_params.get('task') == TASKS_FILTER[1][0]:
            return queryset.filter(
                schedules__status__isnull=True,
                schedules__date=datetime.today().date(),
                schedules__members=request.user
            ).distinct()
        if request.query_params.get('task') == TASKS_FILTER[2][0]:
            return queryset.filter(schedules__status='STOP').distinct()
        return queryset


class DateSearchFilter(filters.SearchFilter):
    search = None

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='search', location='query', required=False, type='string'),
        ]

    def filter_queryset(self, request, queryset, *args, **kwargs):
        search = request.query_params.get(self.search_param, '').strip()
        if search:
            search = self._prepare_search(search)
            self.search = search
            for s in search.replace(',', ' ').split():
                try:
                    dt = parser.parse(s)
                    if dt:
                        if len(s) == 4:
                            self.search = self.search.replace(s, str(dt.year))
                        elif len(s) == 7:
                            self.search = self.search.replace(s, f'{dt.year}-{str(dt.month).rjust(2, "0")}')
                        else:
                            if translation.get_language() == 'en' or dt.day > 12:
                                self.search = self.search.replace(
                                    s, f'{dt.year}-{str(dt.month).rjust(2, "0")}-{str(dt.day).rjust(2, "0")}'
                                )
                            else:
                                self.search = self.search.replace(
                                    s, f'{dt.year}-{str(dt.day).rjust(2, "0")}-{str(dt.month).rjust(2, "0")}'
                                )
                except (ValueError, OverflowError):
                    pass
        return super().filter_queryset(request, queryset, *args, **kwargs)

    def get_search_terms(self, request):
        params = self.search or request.query_params.get(self.search_param, '')
        return params.replace(',', ' ').split()

    @staticmethod
    def _prepare_search(search):
        parsed_dates = re.findall(r'(\d{4}\s\d{2}\s\d{2}|\d{2}\s\d{2}\s\d{4}|\d{2}\s\d{4})', search)
        if parsed_dates:
            for date in parsed_dates:
                clean_date = date.replace(' ', '-')
                search = search.replace(date, clean_date)
        return search.replace('.', '-')
