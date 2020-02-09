from django.conf.urls import url
from apps.medications.views import (
    MedicationsUploadView,
    DrugsViews,
    medications_view
)

urlpatterns = [
    url(r'^(?P<patient_file_id>[0-9]+)$', medications_view, name='medications'),
    url('upload/(?P<filename>[^/]+)/$', MedicationsUploadView.as_view(), name='upload'),
    url('drugs/', DrugsViews.as_view({'get': 'list'}), name='drugs')
]
