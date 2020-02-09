from django.utils import translation

from apps.reports.services import get_report_by_pk
from apps.utils.fields import Base64FileField
from apps.brusafe.services import send_to_brusafe
from apps.patients.models import File
from apps.accounts.models import User
from lifeline.celery import app
from django.conf import settings


@app.task
def report_files_creation(report_pk, report_en, report_fr, report_nl):
    report = get_report_by_pk(report_pk)
    if report:
        report.report_en = Base64FileField().to_internal_value(report_en)
        report.report_fr = Base64FileField().to_internal_value(report_fr)
        report.report_nl = Base64FileField().to_internal_value(report_nl)
        report.save()


@app.task
def brusafe_sending(user_uuid, file_pk, report_type, report_id, report_comment):
    file = File.objects.get(pk=file_pk)
    user = User.objects.get(uuid=user_uuid)
    if file and user:
        for language in settings.MODELTRANSLATION_LANGUAGES:
            with translation.override(language):
                try:
                    send_to_brusafe(user, file, report_type, report_id, report_comment)
                except ConnectionRefusedError as err:
                    print(str(err))
