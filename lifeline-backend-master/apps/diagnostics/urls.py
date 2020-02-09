from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from apps.diagnostics.views import DiagnosticsView, DiagnosisViewSet, HealthScreeningMetaView, DiagnosticsViewSet, \
    DiagnosticAlertsView

router = DefaultRouter()
router.register('diagnosis', DiagnosisViewSet)
router.register('', DiagnosticsViewSet)


urlpatterns = [
    url('file/', DiagnosticsView.as_view(), name='upload_file'),
    url('health-screenings-meta/', HealthScreeningMetaView.as_view({'get': 'list'}), name='health_screening_meta'),
    url('alerts/(?P<file>[0-9]{,10})/', DiagnosticAlertsView.as_view(), name='diagnostic alerts'),
    url('', include(router.urls), name='prescriptions')
]
