import os
import datetime

from rest_framework import serializers
from django.utils.safestring import mark_safe
from rest_framework.parsers import MultiPartParser
from apps.documents.models import DocumentType, Document
from apps.utils.mixins import AwsUrlMixin
from apps.accounts.serializers import UserSerializer
from apps.utils.fields import Base64FileField

date_format = '%d-%m-%Y %H:%M:%S'


class DocumentsTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentType
        fields = ('id', 'name')

class DocumentsSerializer(AwsUrlMixin, serializers.HyperlinkedModelSerializer):
    type_name = serializers.CharField(source='document_type.name', read_only=True)
    document_type = serializers.PrimaryKeyRelatedField(queryset=DocumentType.objects.all())
    author = UserSerializer(read_only=True)
    url_link = serializers.HyperlinkedIdentityField(view_name='documents:download_pdf', read_only=True)
    parser_classes = (MultiPartParser, )
    patient_file = serializers.CharField()
    extension = serializers.CharField(read_only=True)
    file = Base64FileField(max_length=None, use_url=True, required=True, allow_null=False)

    class Meta:
        model = Document
        fields = ('id', 'author', 'patient_file', 'name', 'file', 'url_link', 'document_type', 'type_name', 'created', 'extension')

    def validate(self, data):
        content = data.get('file', None)
        if content is None or content == "":
            raise serializers.ValidationError("Content is required")
        else:
            _, extension = os.path.splitext(content.name)
        # if extension not in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.rtf']:
        #     raise serializers.ValidationError("File is required, expected format: pdf, doc, docx, xls, xlsx, rtf")
        return data
