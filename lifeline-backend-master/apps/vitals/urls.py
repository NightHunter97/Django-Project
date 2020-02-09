from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from apps.vitals.views import VitalsViewSet, VitalTypesView, VitalsChartView, VitalAlertsView

router = DefaultRouter()
router.register('', VitalsViewSet)

urlpatterns = [
    url('types/', VitalTypesView.as_view(), name='types'),
    url('chart/', VitalsChartView.as_view({'get': 'list'}), name='chart'),
    url('alerts/(?P<file>[0-9]{,10})/', VitalAlertsView.as_view(), name='diagnostic alerts'),
    url('', include(router.urls), name='vitals')
]
