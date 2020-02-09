import datetime

from django.core.cache import cache

from rest_framework import filters, status
from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from django.utils.translation import ugettext_lazy as _

from apps.accounts.permissions import LifeLinePermissions
from apps.patients.reader import XslxPatientReader
from apps.patients import choices
from apps.patients.filter_backend import ActivePatientsBackend, StepPatientSearchFilter, FileFilterBackend, \
    SearchStatusPatientsBackend, TaskFilterBackend, OpenStatusSortingBackend, DateSearchFilter
from apps.patients.pagination import PatientFilePagination, EmergencyContactPagination
from apps.patients.serializers import PatientSerializer, FileListSerializer, PatientDetailSerializer, \
    PatientBaseSerializer, ArchiveCommentSerializer, FileStatusSerializer, EmergencyContactSerializer
from apps.patients.services import get_all_files, get_all_patients, get_all_archive_comments, \
    get_file_by_file_id, get_active_emergency_contacts
from apps.patients.tasks import patient_generate_export_file
from apps.units.services import get_all_units
from apps.utils.mixins import DestroyDataMixin


class PatientsViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Returns Patient instances full_name and patient_id fields
    list:
    Returns list of Patient instances containing only full_name and patient_id fields

    create:
    if HTTP_VALIDATION validates data, else creates new patient instance.

    update:
    Updates patient instance from request
    """
    queryset = get_all_patients()
    serializer_class = PatientBaseSerializer
    filter_backends = (StepPatientSearchFilter, )
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    http_method_names = ['post', 'head', 'options', 'patch', 'get']
    lookup_field = 'patient_id'
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PatientSerializer
        return PatientBaseSerializer

    def create(self, request, *args, **kwargs):
        self._mutate_request_data(request)
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        if self.request.META.get('HTTP_VALIDATION'):
            return Response({'Data': 'Valid'}, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.file_id = request.data.get('file_id')
        instance.unit = request.data.get('unit')
        self._mutate_request_data(request)
        self.serializer_class = PatientDetailSerializer
        resp = super().update(request, *args, **kwargs)
        self.serializer_class = PatientBaseSerializer
        return resp

    def _mutate_request_data(self, request):
        request.data.update({
            'death_date': self._clear_empty_strings(request.data.get('death_date')),
            'validity_end': self._clear_empty_strings(request.data.get('validity_end')),
            'email': self._clear_empty_strings(request.data.get('email'))
        })

    @staticmethod
    def _clear_empty_strings(value):
        return value if value else None


class FilesViewSet(ReadOnlyModelViewSet):
    """
    retrieve:
    Returns File and Patient information
    list:
    In results returns list of all Patient from File instances, whether File is closed is based on queary_params
    """
    queryset = get_all_files()
    serializer_class = PatientDetailSerializer
    filter_backends = (
        DateSearchFilter, filters.OrderingFilter, SearchStatusPatientsBackend, TaskFilterBackend, ActivePatientsBackend
    )
    search_fields = (
        'patient__full_name',
        'patient__patient_id',
        'file_id', 'unit__name',
        'patient__birth_date',
        'closed_since',
    )
    ordering_fields = ('patient__full_name', 'created', 'closed_since', 'unit')
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    lookup_field = 'file_id'
    pagination_class = PatientFilePagination

    def get_queryset(self):
        return self.queryset.filter(unit__in=self.request.user.units.all())

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.patient.unit = instance.unit
        instance.patient.file_id = instance.file_id
        instance.patient.is_released = bool(instance.is_released)
        serializer = self.get_serializer(instance.patient)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        self.serializer_class = FileListSerializer
        self.filter_backends += (OpenStatusSortingBackend, )
        if self.request.query_params.get('active') != 'true':
            self.search_fields += ('created',)
        return super().list(request, *args, **kwargs)


class PatientStatusView(UpdateModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    retrieve:
    Returns whether or not patient was discharged, based on file, provided in query_params
    update:
    Updates patient status
    """
    queryset = get_all_files()
    serializer_class = FileStatusSerializer
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    lookup_field = 'file_id'
    http_method_names = ['head', 'options', 'patch', 'get']

    def retrieve(self, request, **kwargs):
        file = kwargs['file_id']
        file = get_file_by_file_id(file)
        if not file:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({'is_released': bool(file.is_released)}, status=status.HTTP_200_OK)


class PatientMetaView(APIView):
    """
    get:
    provides display values of Patient's ChoiceFields.
    """
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        type = request.query_params.get('type')
        metadata = {
            'language': [{'key': item[0], 'value': item[1]} for item in choices.LANGUAGES],
            'gender': [{'key': item[0], 'value': item[1]} for item in choices.SEX if item[0] != 'I'],
            'document_type': [{'key': item[0], 'value': item[1]} for item in choices.DOCUMENT_TYPES],
            'card_type': [{'key': item[0], 'value': item[1]} for item in choices.CARD_TYPES],
            'marital_status': [{'key': item[0], 'value': item[1]} for item in choices.MARITAL_STATUSES],
            'religion': [{'key': item[0], 'value': item[1]} for item in choices.RELIGIONS],
            'dependants': [{'key': item[0], 'value': item[1]} for item in choices.DEPENDANTS],
            'beneficiary_occupation': [{'key': item[0], 'value': item[1]} for item in choices.OCCUPATIONS],
            'income_origin': [{'key': item[0], 'value': item[1]} for item in choices.INCOME_ORIGIN],
            'admission': [{'key': item[0], 'value': item[1]} for item in choices.ADMISSION],
            'education': [{'key': item[0], 'value': item[1]} for item in choices.EDUCATION],
            'edu_pathway': [{'key': item[0], 'value': item[1]} for item in choices.EDUCATION_PATHWAY],
            'insurance_policy': [{'key': item[0], 'value': item[1]} for item in choices.HEALTH_INSURANCE],
            'heading_code': [{'key': item[0], 'value': item[1]} for item in choices.HEADING_HEALTH_INSURANCE],
            'country': [{'key': item[0], 'value': item[1]} for item in choices.COUNTRIES],
            'relations': [{'key': item[0], 'value': item[1]} for item in choices.RELATIONS],
            'units': [{'key': item.id, 'value': item.name} for item in get_all_units()],
            'tasks': [{'key': item[0], 'value': item[1]} for item in choices.TASKS_FILTER]
        }
        return Response(metadata.get(type, metadata), status=status.HTTP_200_OK)


class ArchiveCommentViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    """
    list:
    List of comments in archived file
    create:
    Create new comment to archived file
    """
    queryset = get_all_archive_comments()
    serializer_class = ArchiveCommentSerializer
    filter_backends = (FileFilterBackend,)
    permission_classes = (IsAuthenticated, LifeLinePermissions)


class IsArchiveCommentRequired(APIView):
    """
    get:
    Returns whether or not archive comment is required.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, file_id, **kwargs):
        date_from = datetime.datetime.now() - datetime.timedelta(days=1)
        commented = get_all_archive_comments().filter(file__file_id=file_id, created__gte=date_from).first()
        if commented and commented.user.pk == request.user.pk:
            return Response({'is_comment_required': False})
        return Response({'is_comment_required': True})


class EmergencyContactViewSet(DestroyDataMixin, viewsets.ModelViewSet):
    """
    retrieve:
    Returns EmergencyContact by id
    list:
    Returns EmergencyContact instances for patient, got from file in query_params
    create:
    Creates new EmergencyContact instance
    update:
    Updates EmergencyContact instance
    destroy:
    If reason for deletion is provided, than adds to EmergencyContact instance fields:
    deleted = True
    reason = Reason, specified in request
    If reason is not provided, returns 400 Bad Request
    """
    queryset = get_active_emergency_contacts()
    serializer_class = EmergencyContactSerializer
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    http_method_names = ['post', 'head', 'options', 'patch', 'get', 'delete']
    pagination_class = EmergencyContactPagination

    def get_queryset(self):
        qs_key = str(self.request.user.uuid) + '_emergency_contacts'
        return cache.get(qs_key, get_active_emergency_contacts())

    def list(self, request, *args, **kwargs):
        qs_key = str(self.request.user.uuid) + '_emergency_contacts'
        if 'page' not in request.query_params:
            file = get_file_by_file_id(file_id=request.query_params.get('file'))
            if not file:
                return Response(status=status.HTTP_404_NOT_FOUND)
            queryset = get_active_emergency_contacts().filter(patient=file.patient)
            cache.set(qs_key, queryset, 86400)
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not self.request.data.get('reason'):
            return Response({'reason': _('Specify deletion reason.')}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.reason = self.request.data['reason']
        instance.save(update_fields=['deleted', 'reason'])


class PatientUploadView(APIView):
    """
    post:
    Accepts xlsx document and parses it into Patient model instances, then saves them into DB.
    Allows multiple patient upload.
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (FileUploadParser,)

    def post(self, request, filename):
        reader = XslxPatientReader(request.data['file'], user=request.user)
        reader.proceed()
        error = reader.get_error()
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': 'ok'}, status=status.HTTP_201_CREATED)


class PatientExportView(APIView):
    """
    get:
    Returns a pdf file, containing information about patient
    """
    permission_classes = (IsAdminUser,)
    template_path = 'patients/patient_export_template.html'

    def post(self, request, *args, **kwargs):
        patient_generate_export_file.delay(request.data.get('patient'), request.user.username)
        return Response(status=status.HTTP_200_OK)
