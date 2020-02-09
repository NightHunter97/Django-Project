from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from apps.evaluations.views import EvaluationMetaView, EvaluationsViewSet, SurveyViewSet

router = DefaultRouter()
router.register('survey', SurveyViewSet)
router.register('', EvaluationsViewSet)


urlpatterns = [
    url('meta/', EvaluationMetaView.as_view(), name='meta'),
    url('', include(router.urls), name='evaluations')
]
