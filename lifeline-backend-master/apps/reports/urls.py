from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from apps.reports.views import ReportsViewSet, ReportVisualizeViewSet

router = DefaultRouter()
router.register('visualize', ReportVisualizeViewSet)
router.register('', ReportsViewSet)

urlpatterns = [
    url('', include(router.urls), name='reports'),
]
