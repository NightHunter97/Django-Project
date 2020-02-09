from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from apps._messages.views import MessagesViewSet, AboutPatientViewSet, MessagesMetaView

router = DefaultRouter()
router.register('about', AboutPatientViewSet)
router.register('', MessagesViewSet)


urlpatterns = [
    url('meta/$', MessagesMetaView.as_view(), name='meta_messages'),
    url('', include(router.urls), name='messages'),
]
