import datetime
import uuid

import requests
from django.template.loader import render_to_string

from apps.brusafe.models import Relation
from django.core.cache import cache
from apps.brusafe.constants import SAML_ENDPOINT, BRUSAFE_ENDPOINT, BRUSAFE_CERT
from django.utils import translation

from apps.patients.choices import HEALTH_INSURANCE
from apps.reports.helpers import ReportContextHelper

DOCUMENT_ID_REPLACEMENT = """<rim:Association associationType="urn:ihe:iti:2007:AssociationType:RPLC"
                                id="3c4ec462-265a-4708-aac5-7b4a271203e7"
                                sourceObject="urn:uuid:{}"
                                targetObject={}"/>"""


def patient_user_relation(patient_id, user_uuid):
    return Relation.objects.filter(patient=patient_id, user__uuid=user_uuid).exists()


def get_saml(national_registry, user):
    """Gets saml assertion from Brusafe."""
    token = cache.get(f'{user.uuid}_brusafe')
    response = requests.get(
        f'{SAML_ENDPOINT}/relation-api/api/v1/medical/relation/assertion?national-registry-number='
        f'{national_registry}',
        headers={
            'Authorization': f'Bearer {token}',
        },
        cert=('/lifeline/cert_8.crt', '/lifeline/cert_8.key')
    )
    return response.content


def send_to_brusafe(user, file, report_type, report_id, report_comment):
    """Sends to brusafe patient report.
    :param user: user, who sends report
    :param file: patient file from patient.models
    :param report_type: type of the report
    :param report_id: id of the report
    :param report_comment: comment of the report
    :returns: response from Brusafe.
    Even if errors on brusafe in response, seem to return status_code=200 and sometimes even add/update doc
    """
    document_context = get_document_context(user, file, report_type, report_id, report_comment)
    data = render_to_string('brusafe/document.xml', document_context).encode('utf-8')
    response = requests.post(
        f'{BRUSAFE_ENDPOINT}/services/repository-noxua/',
        data=data,
        headers={
            'Content-Type': 'multipart/related',
            'type': 'text/xml',
            'boundary': str(uuid.uuid4())
        },
        cert=BRUSAFE_CERT
    )
    if response.status_code == 200:
        resp_content = response.content.decode("UTF-8")
        if "SecurityError" in resp_content:
            raise ConnectionRefusedError("SecurityError")
        if "ns3:RegistryError" not in resp_content:
            return response


def get_document_context(user, file, report_type, report_id, report_comment):
    """Fills up document_context dict that will go into document.xml.
    :param user: user, who sends report
    :param file: patient file from patient.models
    :param report_type: type of the report
    :param report_id: id of the report
    :param report_comment: comment of the report
    :returns: dict of all insertions into xml
    """
    report_info = ReportContextHelper.get_specification_context(file)
    doc_id = f'{translation.get_language()}.{uuid.uuid4()}.{report_id}'
    doc_uuid = uuid.uuid4()
    patient = file.patient
    patient.insurance_policy = dict(HEALTH_INSURANCE).get(patient.insurance_policy)
    return {
        'saml': get_saml(file.patient.national_register, user),
        'boundary': uuid.uuid4(),
        'file_created': file.created,
        'unit': file.unit.name,
        'bed': file.bed,
        'patient': patient,
        'doc_id':  doc_id,
        'doc_uuid': doc_uuid,
        'created': datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d%H%M%S'),
        'date_of_report': datetime.datetime.strftime(datetime.datetime.today(), '%d %B %Y'),
        'username': user.username,
        'replace': DOCUMENT_ID_REPLACEMENT.format(doc_uuid, doc_id),
        'report_info': report_info.get(report_type),
        'report_type': report_type,
        'comment': report_comment
    }
