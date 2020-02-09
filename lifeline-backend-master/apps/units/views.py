import datetime

from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.accounts.permissions import LifeLinePermissions
from apps.accounts.services import get_all_users
from apps.patients.serializers import FileListSerializer
from apps.tasks.services import get_today_schedules_for_units, get_due_schedules_for_units, get_my_schedules_for_units
from apps.units.filter_backends import UnitFilterBackend
from apps.units.serializers import UnitSerializer
from apps.units.services import get_all_units, get_unit_patients, get_unit


class UnitsView(ReadOnlyModelViewSet):
    queryset = get_all_units()
    serializer_class = UnitSerializer
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class TasksView(APIView):
    queryset = get_all_units()
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    pagination_class = None

    def get(self, request, *args, **kwargs):
        user_units = request.user.units.all()

        return Response({
            'all_tasks': get_today_schedules_for_units(user_units),
            'my_tasks': get_my_schedules_for_units(user_units, request.user),
            'due_tasks': get_due_schedules_for_units(user_units)
        }, status=status.HTTP_200_OK)


class DashboardView(ReadOnlyModelViewSet):
    serializer_class = FileListSerializer
    queryset = get_all_units()
    permission_classes = (IsAuthenticated, LifeLinePermissions)
    filter_backends = (UnitFilterBackend,)
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset, unit_id = self.filter_queryset(self.get_queryset())
        if not unit_id:
            return Response({'locked': _('Ask admin to create a unit')}, status=status.HTTP_423_LOCKED)

        extents = [
            (datetime.date.today() - file.patient.created.date()).days for file in queryset if not file.is_released
        ]
        all_users = get_all_users()
        unit = get_unit(unit_id)
        return Response({
            'weekly': get_unit_patients(
                qs=queryset, iterations=7, prev_date=datetime.datetime.now()-datetime.timedelta(days=6)
            ),
            'monthly': get_unit_patients(
                qs=queryset, iterations=28, prev_date=datetime.datetime.now()-datetime.timedelta(days=27), step=4
            ),
            'daily': get_unit_patients(
                qs=queryset, iterations=7, prev_date=datetime.datetime.now()-datetime.timedelta(days=1, hours=3),
                step=1, hourly=True
            ),
            'female': len([file for file in queryset.filter(patient__gender='F', unit=unit) if not file.is_released]),
            'male': len([file for file in queryset.filter(patient__gender='M', unit=unit) if not file.is_released]),
            'patients': len([file for file in queryset if not file.is_released]),
            'avg': sum(extents)//len(extents) if extents else 0,
            'occupied': len([file for file in queryset.filter(unit=unit) if not file.is_released]),
            'beds':  unit.beds if unit else 0,
            'doctors': all_users.filter(groups__name='Doctor', units=unit).count(),
            'nurses': all_users.filter(groups__name='Nurse', units=unit).count(),
            'givers': all_users.filter(groups__name='Caregiver', units=unit).count()
        }, status=status.HTTP_200_OK)
