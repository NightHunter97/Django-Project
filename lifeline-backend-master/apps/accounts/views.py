from datetime import date
from dateutil.relativedelta import relativedelta

from django.http import Http404
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework_jwt.views import ObtainJSONWebToken

from apps.accounts.serializers import UserSerializer, UserDetailsSerializer
from apps.accounts.services import get_all_users, get_user_by_uuid, get_log_entry_actions, get_user_activity, \
    get_active_users, clear_brusafe_token
from apps.patients.services import get_archived_files, get_admission_files
from apps.utils.views import BaseExportView
from apps.wish.permissions import WishPermission
from apps.wish.services import create_wish_connection


class UsersViewSet(ReadOnlyModelViewSet):
    """
    get:
    Return a list of all the existing users.
    """
    queryset = get_all_users()
    serializer_class = UserSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)


class UserLanguageView(mixins.CreateModelMixin, GenericViewSet):
    """
    create:
    Updates user-senders first name, last name and language
    """
    http_method_names = ['head', 'options', 'post', 'get']
    queryset = get_all_users()
    serializer_class = UserDetailsSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = UserDetailsSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)


class UserActivityView(BaseExportView):
    """
    get:
    Returns a pdf file, containing information about user activities, depending on the query_params in request
    """
    template_path = 'accounts/activity_report.html'

    @classmethod
    def _get_context(cls, request):
        """
        Prepares context for pdf doc, containing info about user.
        gets from query_params, if present:
        user uuid,
        patient (for user activities about this patient)
        start, end (time period of activities)
        :param request: GET request to view
        :return dict:
        {
            'activities': activities query set for Activity model,
            'user': user to be exported,
            'admin': prepare_admin_logs classmethod
        }
        """
        uuid = request.query_params.get('user')
        patient = request.query_params.get('patient')
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        user = get_user_by_uuid(uuid)
        activities = get_user_activity(user.email, patient, start, end)
        return {'activities': activities, 'user': user, 'admin': cls.prepare_admin_logs(uuid, patient, start, end)}

    @classmethod
    def get_export_name(cls, request):
        return get_user_by_uuid(request.query_params.get('user')) or 'user'

    @classmethod
    def prepare_admin_logs(cls, uuid, patient, start, end):
        """
        Prepares logs for admin actions.
        :param uuid: user to be exported,
        :param patient: for user activities about this patient
        :param start: time period of activities
        :param end: time period of activities
        :return list of tuples:
        For each log in queryset to LogEntry list element:
        (action time, content type, object representation, action_mapping staticmethod, change message)
        """
        qs = get_log_entry_actions(uuid, patient, start, end)
        return [(
            f'{log.action_time.strftime("%B %d, %Y, %I:%M %P")}',
            log.content_type,
            log.object_repr,
            cls.action_mapping(log.action_flag),
            log.change_message.replace('[', '').replace(']', '')
        ) for log in qs]

    @staticmethod
    def action_mapping(action_flag):
        """
        Map of actions
        :param action_flag: action flag
        :return str: action text
        """
        actions = {
            1: 'Created',
            2: 'Changed',
            3: 'Deleted',
        }
        return actions[action_flag]


class UserCommonActivityView(BaseExportView):
    """
    get:
    Returns a pdf file, containing information about common user activities, depending on the query_params in request
    """
    template_path = 'accounts/common_activity_report.html'

    period_map = {
        'month': 1,
        'quarter': 3,
        'year': 12,
        'all': 0
    }

    period_name_display = {
        'month': 'current month',
        'quarter': 'current quarter',
        'year': 'current year',
        'all': 'all the time'
    }

    @classmethod
    def _get_context(cls, request):
        """
        Prepares context for pdf doc, containing info about user.
        gets from query_params, if present:
        user uuid,
        patient (for user activities about this patient)
        start, end (time period of activities)
        :param request: GET request to view
        :return dict:
        {
            'active_files': active patient files,
            'archived_files': archived patient files,
            'user': exporting user,
            'users': active users
        }
        OR
        {
            'active_files': active patient files during time period,
            'archived_files': archived patient files during time period,
            'user': exporting user,
            'users': active users,
            'prev': from timestamp,
            'today': to timestamp
        }
        """
        period = request.query_params.get('period')
        block = request.query_params.get('block')
        if not period or period not in cls.period_map:
            raise Http404
        prev = today = date.today()
        if period == 'month':
            prev = today + relativedelta(day=1)
        elif period == 'quarter':
            prev = date(today.year, (today.month - 1) // 3 * 3 + 1, 1)
        elif period == 'year':
            prev = today + relativedelta(day=1, month=1)
        ctx = {
            'active_files': get_admission_files(),
            'archived_files': get_archived_files(),
            'user': request.user,
            'users': get_active_users(),
            'block': block
        }
        if period == 'all':
            ctx.update({'all': True})
            return ctx
        ctx.update({
            'active_files': get_admission_files().filter(created__date__gte=prev),
            'archived_files': get_archived_files().filter(closed_since__gte=prev),
            'prev': prev,
            'next': today,
        })
        return ctx

    @classmethod
    def get_export_name(cls, request):
        return f"activities {cls.period_name_display.get(request.query_params.get('period'))}"


class ObtainJSONWebTokenClearBrusafeToken(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            os_uuid = request.data.get('os_uuid')
            if os_uuid:
                if not WishPermission().has_permission(user):
                    return Response(status=status.HTTP_403_FORBIDDEN)
                create_wish_connection(user, os_uuid)
            else:
                clear_brusafe_token(user)
        return super().post(request, *args, **kwargs)
