from apps.brusafe.models import Relation
from apps.wish.models import HL7System


def patient_user_relation(patient_id, user_uuid):
    return Relation.objects.filter(patient=patient_id, user__uuid=user_uuid).exists()


def create_wish_connection(user, os_uuid):
    HL7System.objects.get_or_create(user=user, os=os_uuid)
