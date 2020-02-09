from datetime import timedelta

from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from apps.utils.mixins import FileValidationMixin
from apps.vitals.models import VitalsParam


class VitalsSerializer(FileValidationMixin, serializers.ModelSerializer):
    file_id = serializers.CharField(write_only=True)
    file = serializers.CharField(source='file.file_id', read_only=True)
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    type = serializers.CharField(required=False)
    value = serializers.CharField(required=False)
    modified = serializers.SerializerMethodField()

    class Meta:
        model = VitalsParam
        fields = ('value', 'comment', 'type', 'user', 'user_id', 'file_id', 'file', 'id', 'created', 'modified')

    def get_modified(self, obj):
        created = obj.created + timedelta(seconds=1)
        if created < obj.modified:
            return obj.modified


class VitalsChartSerializer(VitalsSerializer):

    class Meta:
        model = VitalsParam
        fields = ('value', 'created')
