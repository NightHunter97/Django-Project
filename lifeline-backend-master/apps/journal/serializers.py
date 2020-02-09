from rest_framework import serializers

from apps.journal.models import Journal
from apps.utils.mixins import FileValidationMixin


class JournalSerializer(FileValidationMixin, serializers.ModelSerializer):
    file_id = serializers.CharField(required=True, write_only=True)
    creator_id = serializers.CharField(source='created_by.uuid', read_only=True)
    created_by = serializers.CharField(source='user', required=False)
    name = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)
    category = serializers.CharField(read_only=True)
    action = serializers.CharField(source='get_action_display', read_only=True)
    tag = serializers.CharField(write_only=True)
    tag_type = serializers.SerializerMethodField()

    class Meta:
        model = Journal
        fields = (
            'name', 'content', 'created_by', 'type', 'file_id', 'created', 'creator_id', 'tag', 'id', 'category',
            'action', 'tag_type'
        )

    def create(self, validated_data):
        validated_data['user'] = self._kwargs['context']['request'].user
        return super().create(validated_data)

    def get_tag_type(self, obj):
        return {'key': obj.tag, 'value': obj.get_tag_display()}
