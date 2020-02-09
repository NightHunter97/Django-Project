import datetime
from dateutil.parser import parse

from django.db.models import Q
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import filters, status

from apps.accounts.permissions import LifeLinePermissions
from apps.medications.serializers import PrescriptionScheduleSerializer
from apps.patients.services import does_file_exist
from apps.tasks.date_periodic_parsers import parse_periodic_data
from apps.tasks.filter_backends import DateFilterBackend, TaskFilterBackend
from apps.tasks.models import Schedule
from apps.tasks.reader import XslxTaskReader
from apps.tasks.serializers import ScheduleSerializer, CategorySerializer, TaskSerializer
from apps.tasks.services import get_all_tasks, get_all_categories, get_all_scheduled_tasks, get_tasks_by_date, \
    get_empty_schedules, get_all_schedules, get_medications_by_date, get_schedule_by_id, \
    delete_all_chained_tasks, tasks_root_update, get_categories_for_user_groups
from apps.utils.mixins import DestroyDataMixin, JournalCommentMixin
from apps.wounds.services import get_wound
from django.utils.translation import ugettext_lazy as _


class TasksViewSet(JournalCommentMixin, DestroyDataMixin, ModelViewSet):
    queryset = get_all_scheduled_tasks()
    serializer_class = ScheduleSerializer
    pagination_class = None
    filter_backends = (DateFilterBackend,)
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete']
    _cached__schedules = []
    _comment_category = _('Planning')
    _comment_slug = 'planning'
    _comment_fields = [
        'task__category__name', '_prescription_cache__task_type', 'task__name', '_prescription_cache__category__term'
    ]

    def get_serializer_context(self):
        if not self._cached__schedules:
            self._cached__schedules = list(get_all_schedules())
        ctx = super().get_serializer_context()
        ctx.update({'_cached__schedules': self._cached__schedules})
        return ctx

    def list(self, request, *args, **kwargs):
        date_string = request.query_params.get('date')
        file_id = request.query_params.get('file')
        if not does_file_exist(file_id):
            return Response({'error': _('File was not found')}, status=status.HTTP_404_NOT_FOUND)
        try:
            date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
            queryset = get_tasks_by_date(date, file_id)
            medications = get_medications_by_date(date, file_id)
        except (ValueError, TypeError):
            queryset = medications = get_empty_schedules()
        serializer = self.get_serializer(queryset.union(medications), context={'request': request}, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        journal = request.data.pop('journal_comment', None)
        if 'status' in request.data and journal:
            self._journal_comment(journal, instance, self.request.user, 'status')
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        res = super().destroy(request, *args, **kwargs)
        if instance.root_id and request.data.get('all') is True:
            return self._bulk_destroy({'root_id': instance.root_id})
        return res

    def _bulk_destroy(self, filter):
        schedules = Schedule.objects.filter(**filter)
        ids = list(schedules.values_list('id', flat=True))
        schedules.delete()
        return Response({'deleted': ids}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        wound = request.data.get('wound')
        root_id = request.data.get('root_id')
        end_date = request.data.get('end_date')
        medication = request.data.get('medication')
        if medication:
            request.data['prescription'] = medication['id']

        data = parse_periodic_data(request.data, user=request.user)
        if len(data) > 300:
            return Response({'repeatMode': [_("Repeats can't be more than 300.")]}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(data, list):
            if medication:
                serializer = PrescriptionScheduleSerializer(data=data, many=True)
            else:
                serializer = self.get_serializer(data=data, many=True)
        else:
            serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        if end_date:
            if parse(request.data['date']) > parse(end_date):
                return Response(
                    {'end_date': [_('Should be later than the chosen date')]}, status=status.HTTP_400_BAD_REQUEST
                )
        self._perform_create(serializer, wound, root_id)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def _perform_create(self, serializer, wound_id, root_id):
        previous_tp = self._clear_previous_tp(wound_id)
        delete_all_chained_tasks(root_id)
        tasks = serializer.save()
        tasks_root_update(self.request.data, tasks)
        if wound_id:
            self._treatment_plan_comment(tasks, previous_tp)

    def _treatment_plan_comment(self, tasks, previous_tp):
        if tasks:
            task = tasks[0] if isinstance(tasks, list) else tasks
            if not previous_tp and task.comment:
                self._comment_category = _('Wounds/Treatment plan')
                self._comment_slug = 'wound'
                self._journal_comment(task.comment, task, self.request.user, 'create')

    @staticmethod
    def _clear_previous_tp(wound_id):
        if wound_id:
            wound = get_wound(wound_id)
            treatment = wound.schedule_set.first()
            if treatment:
                return Schedule.objects.filter(Q(pk=treatment.pk) | Q(root_id=treatment.pk)).delete()


class CategoriesView(ReadOnlyModelViewSet):
    queryset = get_all_categories()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    pagination_class = None

    def get_queryset(self):
        return get_categories_for_user_groups(self.request.user).exclude(slug='medication')


class TaskListViewSet(ReadOnlyModelViewSet):
    queryset = get_all_tasks()
    serializer_class = TaskSerializer
    filter_backends = (TaskFilterBackend, filters.SearchFilter)
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    search_fields = ('name',)
    pagination_class = None


class SuspendScheduleView(JournalCommentMixin, APIView):
    permission_classes = (IsAuthenticated, )
    _comment_category = _('Planning')
    _comment_slug = 'planning'
    _comment_fields = [
        'task__category__name', '_prescription_cache__task_type', 'task__name', '_prescription_cache__category__name'
    ]

    def patch(self, request, pk, **kwargs):
        start = request.data.get('start')
        end = request.data.get('end')
        instance = get_schedule_by_id(pk)
        journal = self.request.data.get('journal_comment')
        self._journal_comment(journal, instance, self.request.user, 'status')
        if not instance:
            return Response({'error': _('Not found')}, status=status.HTTP_404_NOT_FOUND)
        if request.resolver_match.url_name == 'suspend':
            if not start or not end:
                return Response({'error': _('Start and End dates are required')}, status=status.HTTP_400_BAD_REQUEST)
            return self._bulk_suspend(instance, start, end)
        return self._bulk_unsuspend(instance)

    @staticmethod
    def _bulk_suspend(instance, start, end):
        updated = Schedule.objects.filter(
            root_id=instance.root_id, date__gte=start, date__lte=end, status__isnull=True
        ).update(status='SUSP')
        return Response({'updated': updated}, status=status.HTTP_200_OK)

    @staticmethod
    def _bulk_unsuspend(instance):
        Schedule.objects.filter(root_id=instance.root_id, status='SUSP').update(status=None)
        instance.status = None
        return Response(
            ScheduleSerializer(instance, context={'_cached__schedules': list(get_all_schedules())}).data,
            status=status.HTTP_200_OK
        )


class TaskUploadView(APIView):
    """
    post:
    Accepts xlsx document and parses it into Patient model instances, then saves them into DB.
    Allows multiple patient upload.
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (FileUploadParser,)

    def post(self, request, filename):
        reader = XslxTaskReader(request.data['file'], user=request.user, slug=filename)
        reader.proceed()
        error = reader.get_error()
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': 'ok'}, status=status.HTTP_201_CREATED)
