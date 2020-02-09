from django.core.cache import cache

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters

from apps._messages.mixins import UpdateMetaMessageMixin
from apps._messages.permissions import MessagePermissions
from apps._messages.serializers import MessageSerializer, AboutPatientSerializer, MessageDetailSerializer
from apps._messages.services import get_all_messages, get_user_messages, get_empty_messages, \
    get_about_patient_messages, get_all_about_patient_messages
from apps._messages.utils import MessageHelper

from apps.utils.mixins import DestroyDataMixin


class MessagesViewSet(UpdateMetaMessageMixin, DestroyDataMixin, ModelViewSet):
    queryset = get_all_messages()
    serializer_class = MessageSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('subject', 'msg_content', 'sender__first_name', 'sender__last_name')
    permission_classes = (IsAuthenticated, MessagePermissions)
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete']

    def get_queryset(self):
        qs_key = str(self.request.user.uuid) + '_key'
        return cache.get(qs_key, get_empty_messages())

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MessageDetailSerializer
        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user_uuid = request.user.uuid
        if str(user_uuid) not in instance.read_by:
            instance.read_by.append(user_uuid)
            instance.save(update_fields=['read_by'])
        serializer = self.get_serializer(instance)
        response = Response(serializer.data)
        response.data['meta'] = MessageHelper().get_messages(request.user)
        return response

    def list(self, request, *args, **kwargs):
        qs_key = str(self.request.user.uuid) + '_key'
        if 'page' not in request.query_params:
            qs = get_user_messages(self.request.user.pk)
            cache.set(qs_key, qs, 86400)
        return super().list(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.receivers.remove(self.request.user.pk)
        if instance.sender == self.request.user:
            instance.sender = None
            instance.save()

        if not instance.sender and not instance.receivers.all():
            instance.delete()


class AboutPatientViewSet(UpdateMetaMessageMixin, DestroyDataMixin, ModelViewSet):
    queryset = get_all_about_patient_messages()
    serializer_class = AboutPatientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('subject', 'msg_content', 'file__patient__full_name')
    permission_classes = (IsAuthenticated, MessagePermissions)
    http_method_names = ['get', 'head', 'options', 'patch', 'delete']

    def get_queryset(self):
        qs_key = str(self.request.user.uuid) + '_about'
        return cache.get(qs_key, get_empty_messages())

    def list(self, request, *args, **kwargs):
        qs_key = str(self.request.user.uuid) + '_about'
        if 'page' not in request.query_params:
            qs = get_about_patient_messages(self.request.user)
            cache.set(qs_key, qs, 86400)
        return super().list(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.hidden_for.append(str(self.request.user.pk))
        active_users = [
            uuid for uuid in instance.file.unit.user_set.all().values_list('uuid', flat=True)
            if str(uuid) not in instance.hidden_for
        ]
        if active_users:
            instance.save()
        else:
            instance.delete()


class MessagesMetaView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response(MessageHelper().get_messages(request.user))
