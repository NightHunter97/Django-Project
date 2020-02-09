import mimetypes

from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import ModelSerializer
from django.core.cache import cache

from apps._messages.mixins import ReadByMixin
from apps._messages.models import Message, MessageFile, AboutPatient
from apps._messages.utils import MessageHelper
from apps.accounts.serializers import UserSerializer
from apps.accounts.services import get_all_users
from rest_framework import serializers

from apps.utils.fields import Base64FileField
from apps.utils.mixins import AwsUrlMixin


class MessageSerializer(AwsUrlMixin, ModelSerializer):
    receivers = serializers.PrimaryKeyRelatedField(queryset=get_all_users(), many=True, write_only=True)
    files = serializers.ListField(
        required=False, child=Base64FileField(max_length=None, use_url=True)
    )
    message_from = serializers.SerializerMethodField()
    message_to = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            'id',
            'receivers',
            'subject',
            'msg_content',
            'created',
            'read_by',
            'files',
            'message_from',
            'message_to'
        )

    def get_message_from(self, obj):
        if obj.sender == self.context['request'].user:
            return _('You')
        return obj.message_from

    def get_message_to(self, obj):
        receivers = []
        for receiver in obj.message_to:
            if receiver[0] == str(self.context['request'].user.pk):
                receivers.append(str(_('You')))
            else:
                receivers.append(receiver[1])
        return ', '.join(receivers)

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        if not validated_data.get('receivers'):
            raise serializers.ValidationError({'receivers': _('No receivers were chosen')})

        validated_data.update({
            'sender': self.context['request'].user,
            'message_from': str(self.context['request'].user),
            'message_to': [(str(receiver.pk), receiver.username) for receiver in validated_data['receivers']],
            'read_by': [str(self.context['request'].user.uuid)]
        })
        message = super().create(validated_data)
        self._create_message_files(files, message)
        MessageHelper().send(message.receivers.all(), self.context['request'].user)
        return message

    def _create_message_files(self, files, message):
        c_files = []
        for file in files:
            file = MessageFile.objects.create(file=file, message=message)
            base64file = self._get_aws_base64(file.file)
            c_files.append(dict(file=base64file, type=mimetypes.guess_type(file.file.name)[0], name=file.file.name))
        cache.set(f'{message.pk}_message_files', c_files, 86400)


class MessageDetailSerializer(MessageSerializer):
    files_detail = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            'receivers',
            'subject',
            'msg_content',
            'created',
            'id',
            'read_by',
            'files',
            'files_detail',
            'message_from',
            'message_to'
        )

    def get_files_detail(self, obj):
        c_files = cache.get(f'{obj.pk}_message_files') or []
        if not c_files:
            for m_file in MessageFile.objects.filter(message=obj):
                base64file = self._get_aws_base64(m_file.file)
                c_files.append(
                    dict(file=base64file, type=mimetypes.guess_type(m_file.file.name)[0], name=m_file.file.name)
                )
            cache.set(f'{obj.pk}_message_files', c_files, 86400)
        return c_files


class AboutPatientSerializer(ReadByMixin, serializers.ModelSerializer):
    file_id = serializers.SerializerMethodField()
    patient_id = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    user = UserSerializer()

    class Meta:
        model = AboutPatient
        fields = (
            'subject', 'msg_content', 'created', 'id', 'read_by', 'file_id', 'patient_id', 'full_name', 'user'
        )

    @staticmethod
    def get_file_id(obj):
        return obj.file.file_id

    @staticmethod
    def get_patient_id(obj):
        return obj.file.patient.patient_id

    @staticmethod
    def get_full_name(obj):
        return obj.file.patient.full_name
