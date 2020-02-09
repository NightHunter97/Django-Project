from django.conf.urls import url

from apps.brusafe.views import MedicalRelationAssertion, MedicalRelationState, PatientAssertion, \
    MedicalRelationConfirm, MedicalRelationRequest, BrusafeAuthView, UserPatientRelationView, DocumentListView, \
    DocumentView

urlpatterns = [
    url('medical-relation-assertion/', MedicalRelationAssertion.as_view(), name='medical_relation_assertion'),
    url('medical-relation-state/', MedicalRelationState.as_view(), name='medical_relation_state'),
    url('patient-assertion/', PatientAssertion.as_view(), name='patient_assertion'),
    url('medical-relation-confirm/', MedicalRelationConfirm.as_view(), name='medical_relation_confirm'),
    url('medical-relation-request/', MedicalRelationRequest.as_view(), name='medical_relation_request'),

    url('auth/', BrusafeAuthView.as_view(), name='auth'),
    url('relation/', UserPatientRelationView.as_view(), name='relation'),
    url('documents/(?P<national_registry>\\w+)/', DocumentListView.as_view(), name='provide'),
    url('document/(?P<repository_unique_id>(\\w|\\.|\\d)+)/(?P<document_unique_id>(\\w+|\\.|\\d|-)+)/',
        DocumentView.as_view(), name='retrieve'),
]
