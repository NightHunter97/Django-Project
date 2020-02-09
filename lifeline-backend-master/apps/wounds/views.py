from django.core.cache import cache

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.accounts.permissions import LifeLinePermissions
from apps.utils.mixins import DestroyDataMixin, JournalCommentMixin
from apps.wounds import choices
from apps.wounds.filter_backends import IsCuredBackend, WoundEvolutionsBackend
from apps.wounds.serializers import EvolutionSerializer, WoundSerializer
from apps.wounds.services import get_all_wounds, get_all_evolutions, delete_evolution_history, get_empty_evolutions, \
    get_wound_evolutions
from django.utils.translation import ugettext_lazy as _


class WoundsViewSet(JournalCommentMixin, DestroyDataMixin, ModelViewSet):
    queryset = get_all_wounds()
    serializer_class = WoundSerializer
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    filter_backends = (IsCuredBackend,)
    http_method_names = ['head', 'options', 'post', 'patch', 'delete', 'get']
    _comment_category = _('Wounds')
    _comment_slug = 'wound'
    _comment_fields = ['get_type_display', 'name']

    def destroy(self, request, *args, **kwargs):
        if request.query_params.get('evolutions') == 'all':
            instance = self.get_object()
            ids = instance.evolution_set.all().values_list('id', flat=True)
            response = super().destroy(request, skip=True)
            return response or Response(delete_evolution_history(list(ids)[:-1]), status=status.HTTP_200_OK)
        return super().destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save()
        comment = self.request.data.get('comment')
        if self.request.data.get('is_cured') and comment:
            self._journal_comment(comment, self.get_object(), self.request.user, 'cured')


class EvolutionsViewSet(JournalCommentMixin, DestroyDataMixin, ModelViewSet):
    queryset = get_all_evolutions()
    serializer_class = EvolutionSerializer
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    filter_backends = (WoundEvolutionsBackend,)
    http_method_names = ['head', 'options', 'post', 'delete', 'get']
    _comment_category = _('Wounds/Evolution')
    _comment_slug = 'wound'
    _comment_fields = ['get_type_display', 'name']

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, obj=self.get_object().wound, *args, **kwargs)

    def get_queryset(self):
        qs_key = str(self.request.user.uuid) + '_wound'
        return cache.get(qs_key, get_empty_evolutions())

    def list(self, request, *args, **kwargs):
        wound = self.request.query_params.get('wound')
        if 'page' not in request.query_params and wound:
            qs_key = str(self.request.user.uuid) + '_wound'
            cache.set(qs_key, get_wound_evolutions(wound), 86400)
        return super().list(request, *args, **kwargs)


class EvolutionMetaView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        type = request.query_params.get('type')
        metadata = {
            'wounds': [{'key': item[0], 'value': item[1]} for item in choices.WOUND_TYPES],
            'localizations': [{'key': item[0], 'value': item[1]} for item in choices.LOCALIZATION],
        }
        return Response(metadata.get(type, metadata), status=status.HTTP_200_OK)
