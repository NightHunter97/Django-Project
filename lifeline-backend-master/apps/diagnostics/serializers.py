from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from apps.diagnostics.models import Diagnose, HealthScreening, Diagnostic
from apps.patients.services import get_id_by_file_id
from django.utils.translation import ugettext_lazy as _


class DiagnoseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Diagnose
        fields = ('term', 'pk')


class HealthScreeningSerializer(serializers.ModelSerializer):

    class Meta:
        model = HealthScreening
        fields = ('term', 'pk')


class DiagnosticSerializer(serializers.ModelSerializer):
    creator = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)
    file_id = serializers.CharField(write_only=True, required=False)
    name = serializers.SerializerMethodField()

    class Meta:
        model = Diagnostic
        fields = (
            'name', 'creator', 'description', 'type', 'is_allergy', 'created', 'modified', 'id', 'file_id', 'user',
            'diagnose', 'screening'
        )

    def create(self, validated_data):
        file_id = get_id_by_file_id(validated_data['file_id'])
        if not file_id:
            raise serializers.ValidationError({'file_id': _('File not found')})
        validated_data['file_id'] = file_id
        validated_data['creator'] = self._kwargs['context']['request'].user
        validated_data['user'] = self._kwargs['context']['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('file_id', None)
        return super().update(instance, validated_data)

    @staticmethod
    def get_name(obj):
        if obj.is_screening:
            return obj.screening and obj.screening.term
        return obj.diagnose and obj.diagnose.term
