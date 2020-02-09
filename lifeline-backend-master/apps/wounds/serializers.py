from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from apps.utils.fields import Base64FileField
from apps.utils.mixins import AwsUrlMixin, FileValidationMixin
from apps.wounds.models import Wound, Evolution


class EvolutionSerializer(AwsUrlMixin, serializers.ModelSerializer):
    photo = Base64FileField(max_length=None, use_url=True, write_only=True, required=False, allow_null=True)
    photo_url = serializers.SerializerMethodField()
    thumb_url = serializers.SerializerMethodField()
    width = serializers.DecimalField(write_only=True, max_digits=5, decimal_places=2)
    height = serializers.DecimalField(write_only=True, max_digits=5, decimal_places=2)
    evolution_width = serializers.SerializerMethodField()
    evolution_height = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    class Meta:
        model = Evolution
        fields = (
            'width', 'height', 'evolution_width', 'evolution_height', 'photo_url', 'thumb_url', 'photo', 'wound', 'id',
            'created', 'user'
        )

    def create(self, validated_data):
        validated_data['user'] = self._kwargs['context']['request'].user
        return super().create(validated_data)

    def get_photo_url(self, obj):
        return self._get_aws_base64(obj.photo) if obj.photo else None

    def get_thumb_url(self, obj):
        return self._get_aws_base64(obj.thumbnail) if obj.thumbnail else None

    def get_evolution_width(self, obj):
        return obj.width

    def get_evolution_height(self, obj):
        return obj.height


class WoundSerializer(FileValidationMixin, AwsUrlMixin, serializers.ModelSerializer):
    photo = serializers.CharField(write_only=True, required=False, allow_null=True)
    width = serializers.DecimalField(write_only=True, max_digits=5, decimal_places=2)
    height = serializers.DecimalField(write_only=True, max_digits=5, decimal_places=2)
    first_width = serializers.SerializerMethodField()
    first_height = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    thumb_url = serializers.SerializerMethodField()
    file_id = serializers.CharField(write_only=True)
    file = serializers.CharField(source='file.file_id', read_only=True)
    treatment = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    class Meta:
        model = Wound
        fields = (
            'id', 'name', 'type', 'localization', 'is_cured', 'photo', 'width', 'height', 'first_width',
            'first_height', 'photo_url', 'thumb_url', 'file', 'file_id', 'created', 'treatment', 'comment', 'user'
        )

    def create(self, validated_data, **kwargs):
        data = {
            'photo': validated_data.pop('photo', None),
            'width': validated_data.pop('width'),
            'height': validated_data.pop('height')
        }
        validated_data['user'] = self._kwargs['context']['request'].user
        wound = super().create(validated_data)
        data.update({'wound': wound.pk})
        serializer = EvolutionSerializer(data=data, context=self._kwargs['context'])
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return wound

    def get_first_width(self, obj):
        last = obj.evolution_set.last()
        if last:
            return last.width

    def get_first_height(self, obj):
        last = obj.evolution_set.last()
        if last:
            return last.height

    def get_photo_url(self, obj):
        last = obj.evolution_set.last()
        if last and last.photo:
            return self._get_aws_base64(last.photo)

    def get_thumb_url(self, obj):
        last = obj.evolution_set.last()
        if last and last.thumbnail:
            return self._get_aws_base64(last.thumbnail)

    def get_treatment(self, obj):
        task = obj.schedule_set.first()
        if task:
            return task.pk
