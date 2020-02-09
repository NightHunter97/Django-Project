from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from apps.wounds.views import WoundsViewSet, EvolutionsViewSet, EvolutionMetaView

router = DefaultRouter()
router.register('evolutions', EvolutionsViewSet)
router.register('', WoundsViewSet)

urlpatterns = [
    url('meta/', EvolutionMetaView.as_view(), name='meta'),
    url('', include(router.urls), name='wounds')
]
