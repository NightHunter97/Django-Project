from django.utils import translation
from rest_framework import status, filters, mixins
from rest_framework.exceptions import NotAcceptable
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from apps._messages.services import create_about_patient_message
from apps._messages.utils import MessageHelper
from apps.accounts.permissions import LifeLinePermissions
from apps.accounts.services import get_all_users_in_unit
from apps.diagnostics.filter_backends import DiagnosticTypeFilter
from apps.diagnostics.serializers import DiagnoseSerializer, HealthScreeningSerializer, DiagnosticSerializer
from apps.diagnostics.services import get_all_diagnoses, get_all_health_screening, get_all_diagnositcs,\
    get_diagnostics_by_file
from apps.diagnostics.tasks import file_parsing
from apps.utils.filters_backends import StrictSearchFilter
from apps.utils.mixins import DestroyDataMixin, JournalCommentMixin
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

from django.conf import settings


class DiagnosticsView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_mapping = {
        'diagnose': 'proceed_diagnoses',
        'screening': 'proceed_health_screening',
    }

    def post(self, request):
        if any(key not in request.data for key in ("id", "label")):
            raise NotAcceptable
        file_parsing.delay(pk=request.data['id'], type=self.parser_mapping[request.data['label']])
        return Response({'success': _('Parser was started')}, status=status.HTTP_201_CREATED)


class DiagnosisViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = get_all_diagnoses()
    serializer_class = DiagnoseSerializer
    filter_backends = (filters.SearchFilter, StrictSearchFilter)
    search_fields = ('term',)
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    pagination_class = None


class HealthScreeningMetaView(mixins.ListModelMixin, GenericViewSet):
    queryset = get_all_health_screening()
    serializer_class = HealthScreeningSerializer
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    pagination_class = None


class DiagnosticsViewSet(JournalCommentMixin, DestroyDataMixin, ModelViewSet):
    queryset = get_all_diagnositcs()
    serializer_class = DiagnosticSerializer
    filter_backends = (filters.SearchFilter, DiagnosticTypeFilter)
    search_fields = ('diagnose__term', 'screening__term')
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete']
    _comment_category = _('Diagnostics')
    _comment_slug = 'diagnostics'
    _comment_fields = ['get_type_display', 'diagnose__term', 'screening__term']
    about_message_map = dict()

    def create(self, request, *args, **kwargs):
        """
          description: This API creates a diagnostic.
          parameters:
            - name: string
            - description: string
            - type: diagnose, screening, anamnesis
            - is_allergy: boolean
            - file_id: string
          """
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, type='event', *args, **kwargs)

    def get_queryset(self):
        qs_key = str(self.request.user.uuid) + '_diagnostic'
        return cache.get(qs_key, get_all_diagnositcs())

    def list(self, request, *args, **kwargs):
        qs_key = str(self.request.user.uuid) + '_diagnostic'
        if 'page' not in request.query_params:
            queryset = get_all_diagnositcs().filter(
                file__file_id=request.query_params.get('file'), type=request.query_params.get('type')
            )
            cache.set(qs_key, queryset, 86400)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.is_allergy or instance.is_screening:
            self.send_message(instance)
        self._journal_comment(instance.description, instance, self.request.user, 'create', type='event')

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.is_allergy and not self._is_message_sent(instance.pk):
            self.send_message(instance)
        self._journal_comment(instance.description, instance, self.request.user, 'edit', type='event')

    def send_message(self, instance):
        diagnose = instance.screening if instance.is_screening else instance.diagnose
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            with translation.override(lang):
                self.about_message_map[lang] = self._get_subject_name(diagnose, instance)
        create_about_patient_message(
            subject_en=self.about_message_map['en'],
            subject_fr=self.about_message_map['fr'],
            subject_nl=self.about_message_map['nl'],
            msg_content=instance.description,
            file=instance.file,
            user=self.request.user
        )
        MessageHelper().send(get_all_users_in_unit(instance.file.unit.id))
        cache.set(f'diagnostics_message_{instance.pk}', True, 86400)

    @staticmethod
    def _is_message_sent(pk):
        return cache.get(f'diagnostics_message_{pk}')

    @staticmethod
    def _get_subject_name(diagnose, instance):
        return f'{getattr(diagnose, "term", _("Not specified"))}|{instance.get_type_display()}'


class DiagnosticAlertsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, file):
        diagnostics = get_diagnostics_by_file(file)
        alerts = {
            'monitoring': [
                diagnostic.screening.term for diagnostic in diagnostics.filter(type='screening') if diagnostic.screening
            ],
            'allergy': [
                diagnostic.diagnose.term for diagnostic in diagnostics.filter(is_allergy=True) if diagnostic.diagnose
            ],
            'diagnosis': [
                diagnostic.diagnose.term for diagnostic in diagnostics.filter(is_allergy=False) if diagnostic.diagnose
            ],
        }
        return Response(alerts, status=status.HTTP_200_OK)
