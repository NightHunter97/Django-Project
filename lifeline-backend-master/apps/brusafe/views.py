from datetime import datetime

import requests
from django.conf import settings

from django.db import IntegrityError
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache

from apps.accounts.permissions import BrusafePermissions
from apps.accounts.serializers import UserSerializer
from apps.brusafe.constants import BRUSAFE_ENDPOINT, BRUSAFE_CERT
from apps.brusafe.mixins import BrusafePutDataMixin, BrusafeGetDataMixin
from apps.brusafe.models import Relation
from apps.brusafe.services import get_saml
from apps.brusafe.xml_parser import get_documents, parse_inner_cda, parse_cda
from apps.patients.services import get_patient
from django.utils.translation import ugettext_lazy as _


class MedicalRelationAssertion(BrusafeGetDataMixin, APIView):
    permission_classes = (IsAuthenticated, BrusafePermissions)
    endpoint_url = 'relation-api/api/v1/medical/relation/assertion'
    api_headers = {}


class MedicalRelationState(BrusafeGetDataMixin, APIView):
    permission_classes = (IsAuthenticated, BrusafePermissions)
    endpoint_url = 'relation-api/api/v1/medical/relation/state'
    api_headers = {}


class PatientAssertion(BrusafeGetDataMixin, APIView):
    permission_classes = (IsAuthenticated, BrusafePermissions)
    endpoint_url = 'relation-api/api/v1/patient/assertion'
    api_headers = {}


class MedicalRelationConfirm(BrusafePutDataMixin, APIView):
    permission_classes = (IsAuthenticated, BrusafePermissions)
    endpoint_url = 'relation-api/api/v1/medical/relation/confirm'
    api_headers = {}


class MedicalRelationRequest(BrusafePutDataMixin, APIView):
    permission_classes = (IsAuthenticated, BrusafePermissions)
    endpoint_url = 'relation-api/api/v1/medical/relation/request'
    api_headers = {}


class BrusafeAuthView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        expiration = request.data.get('expiration', '28800')
        if token and expiration.isdigit():
            cache.set(f'{request.user.uuid}_brusafe', token, int(expiration))
            return Response(UserSerializer(request.user).data)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserPatientRelationView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        patient_id = request.data.get('patient_id')
        patient = get_patient(patient_id)
        try:
            Relation.objects.create(patient=patient, user=request.user)
            return Response({'valid': 'ok'}, status=status.HTTP_200_OK)
        except IntegrityError:
            return Response({'error': _('IntegrityError')}, status=status.HTTP_400_BAD_REQUEST)


class DocumentListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, national_registry, *args, **kwargs):
        response = requests.post(
            f'{BRUSAFE_ENDPOINT}/services/registry-noxua/1.3.6.1.4.1.48336.1/',
            data=render_to_string('brusafe/list.xml', {
                'national_registry': national_registry,
                'created': datetime.now()
            }),
            cert=BRUSAFE_CERT
        )
        return Response({'document_set': get_documents(response.content)}, status=response.status_code)


class DocumentView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, repository_unique_id, document_unique_id, *args, **kwargs):
        national_registry = request.query_params.get('national_registry')
        saml = get_saml(national_registry, request.user)
        response = requests.post(
            f'{BRUSAFE_ENDPOINT}/services/repository-noxua/',
            headers={
                'Content-Type': 'application/xop+xml',
                'type': 'text/xml',
            },
            data=render_to_string('brusafe/get_document.xml', {
                'saml': saml,
                'RepositoryUniqueId': repository_unique_id,
                'DocumentUniqueId': document_unique_id,
            }).encode('utf-8'),
            cert=BRUSAFE_CERT
        )

        if response.status_code == 200 and "SecurityError" in str(response.content):
            return Response(data="SecurityError", status=status.HTTP_403_FORBIDDEN)

        if document_unique_id.lower().startswith(settings.MODELTRANSLATION_LANGUAGES):
            return Response(
                {'document': parse_inner_cda(response.content.decode("utf-8"))},
                status=response.status_code)
        return Response(
            {'document': parse_cda(response.content.decode("utf-8"))},
            status=response.status_code)
