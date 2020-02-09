from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from apps.accounts.permissions import LifeLinePermissions
from apps.utils.mixins import DestroyDataMixin, JournalCommentMixin
from apps.vitals import choices
from apps.vitals.chart_parser import get_parsed_data
from apps.vitals.filter_backends import VitalsFilterBackend
from apps.vitals.serializer import VitalsSerializer, VitalsChartSerializer
from apps.vitals.services import get_all_vitals, get_last_vitals_by_file
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache


class VitalsViewSet(JournalCommentMixin, DestroyDataMixin, ModelViewSet):
    queryset = get_all_vitals()
    serializer_class = VitalsSerializer
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    filter_backends = (VitalsFilterBackend, )
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete']
    _comment_category = _('Vital parameters')
    _comment_slug = 'vitals'
    _comment_fields = ['get_type_display']

    def get_queryset(self):
        qs_key = str(self.request.user.uuid) + '_vitals'
        return cache.get(qs_key, get_all_vitals())

    def list(self, request, *args, **kwargs):
        qs_key = str(self.request.user.uuid) + '_vitals'
        if 'page' not in request.query_params:
            queryset = get_all_vitals().filter(
                file__file_id=request.query_params.get('file'), type=request.query_params.get('type')
            )
            cache.set(qs_key, queryset, 86400)
        return super().list(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        kwargs = self._prepare_data(kwargs)
        return self.serializer_class(*args, **kwargs)

    def _prepare_data(self, kwargs):

        if not self.request.data:
            return kwargs

        params = self.request.data.get('params')
        if params and isinstance(params, list):
            kwargs['data'] = [{**kwargs['data'], **param, 'user_id': self.request.user.pk}
                              for param in params if param.get('value')]
            kwargs['many'] = True
        else:
            kwargs['data']['user_id'] = self.request.user.pk
        return kwargs

    def perform_create(self, serializer):
        instance = serializer.save()
        action = 'add'
        if isinstance(instance, list):
            instance, action, self._comment_fields = instance[0], 'create', []
        self._journal_comment(instance.comment, instance, self.request.user, action)


class VitalsChartView(ReadOnlyModelViewSet):
    queryset = get_all_vitals()
    serializer_class = VitalsChartSerializer
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    filter_backends = (VitalsFilterBackend, )
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        from_date = request.query_params.get('from')
        to = request.query_params.get('to')
        tz = self.request.META.get('HTTP_TZINFO')
        serializer = self.get_serializer(get_parsed_data(queryset, from_date, to, tz), many=True)
        return Response(serializer.data)


class VitalTypesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response(
            [{
                'id': item[0],
                'value': item[1],
                'slug': choices.VITAL_TYPES_SLUGS_MAP[item[0]],
                'unit': choices.VITAL_UNITS_MAPPING[item[0]]
            } for item in choices.VITAL_TYPES], status=status.HTTP_200_OK
        )


class VitalAlertsView(APIView):
    permission_classes = (IsAuthenticated,)
    params = ('weight', 'pressure', 'temp', 'sugar')

    def get(self, request, file):
        return Response(self._prepate_data(file), status=status.HTTP_200_OK)

    def _prepate_data(self, file):
        return get_last_vitals_by_file(file, self.params)
