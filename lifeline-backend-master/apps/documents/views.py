import uuid
import os
import requests
import base64

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.documents.models import DocumentType, Document
from .serializers import DocumentsTypeSerializer, DocumentsSerializer
from apps.utils.mixins import AwsUrlMixin
from apps.accounts.permissions import LifeLinePermissions
from apps.patients.models import Patient, File
from apps.accounts.models import User
from apps.documents.services import get_all_document_types, get_all_documents
from apps.documents.filter_backends import FileFilterBackend

from xhtml2pdf import pisa
import io
import apps.documents.rtf.Rtf2Html as rtf
from pydocx import PyDocX
from django.core.files.base import ContentFile

class DocumentTypeListView(generics.ListAPIView):
    """ Doctype list view"""
    queryset = get_all_document_types()
    serializer_class = DocumentsTypeSerializer
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    pagination_class = None

class DocumentsView(viewsets.ModelViewSet, AwsUrlMixin):
    """ Document instance view
        url endpoint: `api/v1/documents/`

        POST method:
          req data payload:
            {
              "file": <BASE64>
              "patient_file": <pk string>
              "author_id": <pk string>
              "document_type": <pk string>
              "name": <string>
            }
           query_params: ?patient_file_id=<string>

        response data (after POST and GET method paginated `results`):
          {
            "id": <pk string>,
            "author": {
                "username": <string>,
                "pk": <pk string>
            },
            "patient_file": <pk string>,
            "name": <string>,
            "file": <url string>,
            "url_link": <url string>,
            "document_type": <pk string>,
            "created": <date time ISO string>
          }
    """
    queryset = get_all_documents()
    serializer_class = DocumentsSerializer
    http_method_names = ['post', 'get']
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    filter_backends = (FileFilterBackend,)
    pagination_class = None

    def list(self, request, *args, **kwargs):
        data = super().list(request, *args, **kwargs).data
        return Response({ 'results': data })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, request.data['file'])
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, original_file):
        patient_file = File.objects.get(file_id=serializer.validated_data['patient_file'])
        if patient_file is None:
            raise ValidationError('Patient with this id fields doesnt exist')
        serializer.save(author=self.request.user, patient_file=patient_file)

class DownloadView(AwsUrlMixin, generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    queryset = Document.objects.all()

    def get(self, request, *args, **kwargs):
        file = get_object_or_404(Document, pk=self.kwargs["pk"])

        return Response({'url': self._get_aws_url(file.file, 5)}, status=status.HTTP_200_OK)


class PreviewView(generics.CreateAPIView, AwsUrlMixin):
    """ Preview pdf file
        url endpoint: `api/v1/document/preview`
        POST method:
          request data payload:
            {
              document_id: <pk string>
            }
          response data:
            {
              preview: <BASE64>,
              extention: <string>,
              title: <string>
            }
    """

    def create(self, request, *args, **kwargs):
        file = get_object_or_404(Document, pk=request.data['document_id'])
        preview = self._create_pdf(file)
        return preview

    def _create_pdf(self, file):
        _, extension = os.path.splitext(file.file.name)
        aws_response = requests.get(self._get_aws_url(file.file, 5))
        content = ContentFile(aws_response.content)

        if extension in ['.xlsx', '.xls', '.xlb']:
            preview_file = f'preview;name;data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(content.read()).decode("utf-8")}'
            return Response({'preview': preview_file, 'extension': extension, 'title': file.name}, status=status.HTTP_200_OK)
        elif extension == '.pdf':
            preview_file = f'preview;name;data:application/pdf;base64,{base64.b64encode(content.read()).decode("utf-8")}'
            return Response({'preview': preview_file, 'extension': extension, 'title': file.name}, status=status.HTTP_200_OK)
        elif extension == '.docx':
            html = PyDocX.to_html(content)
        elif extension == '.rtf':
            html = rtf.getHtml(content.read().decode('UTF-8'))
        else:
            raise ValidationError("File is required, expected format: pdf, doc, docx, xls, xlsx, rtf")
        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        pisa.CreatePDF(html, dest=response)
        preview_file = f'preview;name;data:application/pdf;base64,{base64.b64encode(response.content).decode("utf-8")}'
        return Response({'preview': preview_file, 'extension': extension, 'title': file.name}, status=status.HTTP_200_OK)



