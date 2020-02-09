from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, filters, mixins
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from apps.accounts.permissions import LifeLinePermissions
from apps.units.models import Unit
from apps.patients.models import File

from .models import Prescription
from .reader import CSVReader
from .filter_backends import MedicationIntakesBackend

from .serializers import (
    PrescriptionSerializer,
    MedicationIntakeSerializer,
    DrugSerializer,
    TimeSlotSerializer
)

from .services import get_all_intakes, get_all_drugs

class DrugsViews(mixins.ListModelMixin, GenericViewSet):
    queryset = get_all_drugs()
    serializer_class = DrugSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAuthenticated,)
    pagination_class = None


class MedicationsUploadView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (FileUploadParser,)

    def post(self, request, filename):
        reader = CSVReader(request.data['file'])
        reader.proceed()
        if reader.error:
            return Response(reader.error, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': 'ok'}, status=status.HTTP_201_CREATED)


class MedicationIntakeSet(mixins.ListModelMixin, GenericViewSet):
    queryset = get_all_intakes()
    serializer_class = MedicationIntakeSerializer
    filter_backends = (MedicationIntakesBackend,)
    permission_classes = (IsAuthenticated, LifeLinePermissions)


@permission_classes([LifeLinePermissions])
@api_view(['GET', 'POST'])
def medications_view(*args, **kwargs):
    """ # `medications/<patient_file_id>`
        ## GET/CREATE Medication (composite of `TimeSlot/Prescription/MedcationIntake` models)
        ### Require `patient_file_id` slug
        ### Require POST req data payload (for `PrescriptionSerializer` & `TimeSlotSerializer`):
        ### extra permissions: `request.user` should be related to `patient_file_id` unit
        ### test suite cmd: `python3 manage.py test apps.medications.tests`
    """
    try:
        request = args[0]
        user = request.user

        patient_file_id = kwargs['patient_file_id']
        patient_file = File.objects.get(file_id=patient_file_id)

        unit = Unit.objects.get(id=patient_file.unit.id)
        has_access = bool(user.units.filter(id=unit.id))

        if not has_access:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if request.method == 'GET':
            queryset = Prescription.objects.filter(file=patient_file.pk)
            data = PrescriptionSerializer(queryset, many=True).data
            return Response(data, status=status.HTTP_200_OK)

        if request.method == 'POST':
            data = request.data
            time_slots_payload = data.pop('timeSlots')

            prescription_data = {
                **data,
                'file': patient_file.pk,
                'creator': user.username
            }

            prescription_serializer = PrescriptionSerializer(data=prescription_data)
            prescription_serializer.is_valid(raise_exception=True)
            prescription = prescription_serializer.save()

            time_slots_data = list(map(
                lambda x: {**x, 'prescription': prescription.id},
                time_slots_payload
            ))

            time_slots_serializer = TimeSlotSerializer(
                data=time_slots_data, many=True
            )
            time_slots_serializer.is_valid(raise_exception=True)
            time_slots_serializer.save()

            return Response(prescription_serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    except BaseException as error:
        return Response(str(error), status=status.HTTP_400_BAD_REQUEST)
