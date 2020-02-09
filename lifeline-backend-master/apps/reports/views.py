import base64

import requests
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.cache import cache
from django.utils import translation
from django.conf import settings
from django.utils.translation import get_language
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from xhtml2pdf import pisa

from apps.accounts.permissions import LifeLinePermissions
from apps.patients.choices import HEALTH_INSURANCE
from apps.patients.services import get_file_by_file_id
from apps.reports.choices import REPORT_TYPE
from apps.reports.filter_backends import FileFilterBackend
from apps.reports.helpers import ReportContextHelper
from apps.reports.serializers import ReportSerializer, VisualizeReportSerializer, ReportListSerializer
from apps.reports.services import get_all_reports, get_current_time_zone_datetime, get_report_logo
from apps.utils.mixins import AwsUrlMixin


class ReportsViewSet(ModelViewSet):
    queryset = get_all_reports()
    serializer_class = ReportSerializer
    http_method_names = ('get', 'post', 'head', 'options')
    permission_classes = (IsAuthenticated, LifeLinePermissions)

    def list(self, request, *args, **kwargs):
        self.filter_backends = (FileFilterBackend,)
        self.serializer_class = ReportListSerializer
        return super().list(request, *args, **kwargs)


class ReportVisualizeViewSet(AwsUrlMixin, ModelViewSet):
    serializer_class = VisualizeReportSerializer
    template_path = 'reports/base_report.html'
    queryset = get_all_reports()
    http_method_names = ('post', 'head', 'options')
    permission_classes = (IsAuthenticated, LifeLinePermissions)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self._get_serializer_data())
        serializer.is_valid(raise_exception=True)
        self._set_multi_language_reports_cache(request)
        return Response({
            'report': cache.get(
                f'{request.user.uuid}|{request.data["file"]}|{get_language()[:2]}'), **serializer.data
            },
            status=status.HTTP_200_OK
        )

    def _set_multi_language_reports_cache(self, request):
        for language in settings.MODELTRANSLATION_LANGUAGES:
            with translation.override(language):
                cache.set(f'{request.user.uuid}|{request.data["file"]}|{language}',
                          f'{request.data["type"]}|{self._get_report_file()}', 86400)
        cache.set(f'{request.user.uuid}|{request.data["file"]}|comment',
                  f'{request.data["comment"]}', 86400)

    def _get_serializer_data(self):
        return {
            'file': self.request.data.get('file'),
            'type': self.request.data.get('type'),
            'comment': self.request.data.get('comment')
        }

    def _get_report_file(self):
        logo = get_report_logo()
        response = requests.get(url=self._get_aws_url(logo) if logo else self._get_default_logo())
        ctx = self._get_context(response)
        html = get_template(self.template_path).render(ctx)
        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        pisa.CreatePDF(html, dest=response)
        return f'report;name;data:application/pdf;base64,{base64.b64encode(response.content).decode("utf-8")}'

    def _get_context(self, response):
        file = get_file_by_file_id(self.request.data['file'])
        if not file:
            return {}
        patient = file.patient
        patient.insurance_policy = dict(HEALTH_INSURANCE).get(patient.insurance_policy)
        ctx = {
            'created': get_current_time_zone_datetime(),
            'type': dict(REPORT_TYPE)[self.request.data['type']],
            'comment_lines': self.request.data.get('comment', '').split('\n'),
            'logo': f'data:image/jpeg;base64,{base64.b64encode(response.content).decode("utf-8")}',
            'username': self.request.user,
            'patient': patient,
            'file_created': file.created,
            'unit': file.unit.name,
            'bed': file.bed,
        }
        ctx.update(ReportContextHelper.get_specification_context(file)[self.request.data['type']])
        self.template_path = f'reports/{self.request.data["type"]}_report.html'
        return ctx

    def _get_default_logo(self):
        if settings.TRANSFER_PROTOCOL == 'http':
            return f'{settings.TRANSFER_PROTOCOL}://' \
                   f'{self.request.META["HTTP_HOST"]}{static("reports/default_logo.jpg")}'
        return static('reports/default_logo.jpg')
