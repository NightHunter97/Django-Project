from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from apps.journal.views import JournalViewSet, JournalMetaView

router = DefaultRouter()
router.register('', JournalViewSet)

urlpatterns = [
    url('meta/', JournalMetaView.as_view(), name='meta'),
    url('', include(router.urls), name='wounds')
]
