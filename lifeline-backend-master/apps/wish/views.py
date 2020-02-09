from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.wish.serializers import PatientFromHL7Serializer, FileHL7Serializer
from apps.patients.services import get_patient_by_nr, get_active_patient_file, get_last_closed_patient_file
from apps.wish.hl7_parser import parse_hl7_file
from apps.wish.permissions import OsAuthenticated


class WishView(APIView):
    permission_classes = (OsAuthenticated,)

    def post(self, request, *args, **kwargs):
        hl7_file = request.data.get('upload_file')
        if hl7_file:
            file_data = hl7_file.readlines()
            message_list = parse_hl7_file(file_data)

            if not message_list:
                return Response(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, data=_('No data was parsed.'))

            for message in message_list:
                patient_info, visit_info = self._get_info(message)

                patient = get_patient_by_nr(message["national_register"])

                if patient_info:
                    self._update_patient_profile(patient, patient_info)

                if visit_info:
                    patient_file = get_active_patient_file(patient)
                    if "A13" in str(visit_info.get("action")):
                        patient_file = get_last_closed_patient_file(patient)
                    self._update_patient_file(patient_file, visit_info)

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def _get_info(message):
        """Splits message into multiple dicts for convenience."""
        patient_info = message.get("patient_info")
        visit_info = message.get("visit_info")
        insurance_info = message.get("insurance_info")
        if patient_info:
            if visit_info:
                patient_info.update(visit_info)
            if insurance_info:
                patient_info.update(insurance_info)

        return patient_info, visit_info

    @staticmethod
    def _update_patient_profile(patient, patient_info):
        """Run create/update of the patient"""
        patient_serializer = PatientFromHL7Serializer(instance=patient, data=patient_info)
        patient_serializer.is_valid(raise_exception=True)
        patient_serializer.save()

    @staticmethod
    def _update_patient_file(patient_file, visit_info):
        """Run update of the patient"""
        if patient_file:
            file_serializer = FileHL7Serializer(instance=patient_file, data=visit_info)
            file_serializer.is_valid(raise_exception=True)
            file_serializer.save()
