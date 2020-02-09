import base64
import mimetypes

import boto3
import requests
from django.utils import translation
from rest_framework import status, serializers
from rest_framework.response import Response
from django.conf import settings

from apps.journal.services import create_journal_message
from apps.patients.services import get_file_by_file_id, get_id_by_file_id
from django.utils.translation import ugettext_lazy as _


class DestroyDataMixin:
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_pk = instance.pk
        file = getattr(instance, 'file', None)
        self.perform_destroy(instance)
        return Response({
            'id': instance_pk, 'patient_id': file.patient.patient_id if file else None
        }, status=status.HTTP_200_OK)


class JournalCommentMixin:
    journal_name_map = {
        'en': '',
        'fr': '',
        'nl': ''
    }

    def destroy(self, request, *args, **kwargs):
        comment = request.data.get('journal_comment')
        if not comment:
            return Response({'error': _('Comment is required')}, status=status.HTTP_400_BAD_REQUEST)
        self._journal_comment(comment, kwargs.get('obj') or self.get_object(), request.user, 'delete', **kwargs)
        if not kwargs.get('skip'):
            return super().destroy(request, *args, **kwargs)

    def _name_generator(self, instance):
        names_list = [str(self._comment_category)]
        for field in self._comment_fields:
            split_values = field.split('__')
            attr = getattr(instance, split_values[0], None)
            obj = attr() if callable(attr) else attr
            if not obj:
                continue
            for value in split_values[1:]:
                obj = getattr(obj, value)
            names_list.append(str(obj))
        return '/'.join(names_list)

    def _journal_comment(self, message, instance, user, action, **kwargs):
        if message:
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                with translation.override(lang):
                    self.journal_name_map[lang] = self._name_generator(instance)
            create_journal_message(
                self.journal_name_map['en'],
                self.journal_name_map['fr'],
                self.journal_name_map['nl'],
                message, get_file_by_file_id(instance.file.file_id) if instance else None,
                user, self._comment_slug, action, **kwargs
            )


class AwsUrlMixin:
    def _get_aws_url(self, url, exp = 86400):
        if not settings.AWS_ACCESS_KEY_ID:
            return url

        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        params = {'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': f'{settings.AWS_STORAGE_LOCATION}/{url}'}
        return s3_client.generate_presigned_url('get_object', Params=params, ExpiresIn=exp)

    def _get_aws_base64(self, file):
        response = requests.get(url=self._get_aws_url(file))
        return f'data:{mimetypes.guess_type(file.file.name)[0]};' \
               f'base64,{base64.b64encode(response.content).decode("utf-8")}'


class FileValidationMixin:
    def validate_file_id(self, file_id):
        file_pk = get_id_by_file_id(file_id)
        if not file_pk:
            raise serializers.ValidationError(_('File not found'))
        return file_pk
