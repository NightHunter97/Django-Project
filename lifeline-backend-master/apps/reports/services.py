import pytz
from datetime import datetime

from django.utils import timezone

from apps.reports.models import Logo, Report


def get_report_logo():
    logo = Logo.objects.last()
    if logo:
        return logo.image


def get_all_reports():
    return Report.objects.all()


def get_report_by_pk(pk):
    return Report.objects.filter(pk=pk).first()


def get_current_time_zone_datetime():
    return datetime.now().astimezone(pytz.timezone(timezone.get_current_timezone_name()))
