import base64

import requests
from rest_framework import serializers
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.patients.services import get_file_by_file_id
from apps.reports.models import Report
from apps.reports.tasks import report_files_creation, brusafe_sending
from apps.utils.mixins import AwsUrlMixin


class ReportSerializer(AwsUrlMixin, serializers.ModelSerializer):
    report_file = serializers.SerializerMethodField()
    file = serializers.CharField()
    title = serializers.SerializerMethodField()
    report_map = {
        'report_en': None,
        'report_fr': None,
        'report_nl': None
    }
    report_type = None

    class Meta:
        model = Report
        fields = ('file', 'report_file', 'pk', 'title')

    @staticmethod
    def validate_file(file):
        return get_file_by_file_id(file)

    @staticmethod
    def get_title(obj):
        return f'{obj.get_type_display()} / {obj.title}'

    def get_report_file(self, obj):
        if obj.report:
            response = requests.get(url=self._get_aws_url(obj.report))
            return base64.b64encode(response.content)

    def create(self, validate_data):
        user = self._kwargs['context']['request'].user
        is_brusafe = self._kwargs['context']['request'].data.get('is_brusafe')
        validate_data['creator'] = user
        for language in settings.MODELTRANSLATION_LANGUAGES:
            file_data = cache.get(f'{user.uuid}|{validate_data["file"]}|{language}')
            if not file_data:
                raise serializers.ValidationError({'report_file': _('Document was expired')})
            cache.set(f'{user.uuid}|{validate_data["file"]}|{language}', None, 0)
            self.report_map[f'report_{language}'] = file_data.split('|')[1]
            self.report_type = file_data.split('|')[0]
        report_comment = cache.get(f'{user.uuid}|{validate_data["file"]}|comment') or ""
        cache.set(f'{user.uuid}|{validate_data["file"]}|comment', None, 0)
        validate_data['type'] = self.report_type
        instance = super().create(validate_data)
        report_files_creation.delay(instance.pk, **self.report_map)
        if is_brusafe:
            brusafe_sending.delay(user.uuid, instance.file.pk, self.report_type, instance.pk, report_comment)
        return instance


class ReportListSerializer(AwsUrlMixin, serializers.ModelSerializer):
    file = serializers.CharField(source='file.file_id')
    title = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ('file', 'title', 'pk')

    @staticmethod
    def get_title(obj):
        return f'{obj.get_type_display()} / {obj.title}'


class VisualizeReportSerializer(AwsUrlMixin, serializers.ModelSerializer):
    file = serializers.CharField()
    comment = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Report
        fields = ('file', 'type', 'comment')
