from collections import OrderedDict

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.accounts.permissions import LifeLinePermissions
from apps.evaluations.filter_backends import FileFilterBackend, TypeFilterBackend, SurveyTypesFilterBackend
from apps.evaluations.pagination import EvaluationsPagination
from apps.evaluations.serializers import EvaluationsSerializer, SurveyLightSerializer, EvaluationsBaseSerializer, \
    SurveySerializer
from apps.evaluations.services import get_all_evaluations, get_enabled_surveys_for_user_groups, \
    get_all_surveys, get_all_evaluations_for_file, get_survey_by_id, check_user_permissions


class EvaluationsViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Returns either Evaluation object for view or, if is_edit Survey object with previous results for prefill

    list:
    For active evaluations returns all Evaluation objects
     with same survey_type as survey_type from request.query_params.
    For archived evaluations returns all Evaluation objects with same name as survey_type from request.query_params.

    create:
    Creates new Evaluation object from request.
    """
    queryset = get_all_evaluations()
    serializer_class = EvaluationsSerializer
    filter_backends = (FileFilterBackend, TypeFilterBackend)
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    http_method_names = ['post', 'head', 'options', 'get']
    pagination_class = EvaluationsPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EvaluationsSerializer
        return EvaluationsBaseSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.query_params.get('is_edit'):
            user = request._user
            if not instance.is_editable or not (
                    check_user_permissions(user, instance.survey_type.id) or user.is_superuser
            ):
                return Response(status=status.HTTP_404_NOT_FOUND)
            instance.survey_type.survey_results = instance.survey_results
            instance.survey_type.evaluation_id = instance.id
            serializer = SurveySerializer(instance.survey_type)
            return Response(serializer.data)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        responce = super().list(request, *args, **kwargs)
        survey_type = request.query_params.get('survey_type')
        try:
            survey_type = int(survey_type)
        except ValueError:
            pass

        try:
            if isinstance(survey_type, int):
                responce.data.update({'survey_name': get_survey_by_id(survey_id=survey_type).name})
            else:
                responce.data.update({'survey_name': survey_type})
        except (KeyError, AttributeError):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return responce

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class SurveyViewSet(ReadOnlyModelViewSet):
    """
    retrieve:
    Returns detailed Survey object.

    list:
    Returns list of Survey objects containing only names and ids
    """
    queryset = get_all_surveys()
    serializer_class = SurveySerializer
    filter_backends = (SurveyTypesFilterBackend, )
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    http_method_names = ['head', 'options', 'get']
    pagination_class = None

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = SurveySerializer
        instance = self.get_object()
        user = request._user
        if not (check_user_permissions(user, instance.id) or user.is_superuser):
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        self.serializer_class = SurveyLightSerializer
        responce = super().list(request, *args, **kwargs)
        if bool(request.query_params.get('archive')):
            file_id = request.query_params.get('file')
            old_evals = get_all_evaluations_for_file(file_id=file_id).filter(survey_type__isnull=True).order_by('name').distinct('name')
            names = [cat.get('survey_name') for cat in responce.data]
            for res in old_evals:
                if res.name not in names:
                    responce.data.append(OrderedDict([('survey_name', res.name)]))
        return responce


class EvaluationMetaView(APIView):
    """
    get:
    Returns list of Survey objects containing only names and ids
    """
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        return Response(data=SurveyLightSerializer(instance=get_enabled_surveys_for_user_groups(request.user),
                                                   many=True).data)
