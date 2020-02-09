from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from apps.tasks.views import TasksViewSet, CategoriesView, TaskListViewSet, SuspendScheduleView, TaskUploadView

router = DefaultRouter()
router.register('subcategories', TaskListViewSet)
router.register('', TasksViewSet)


urlpatterns = [
    url('^categories/', CategoriesView.as_view({'get': 'list'}), name='categories'),
    url('upload/(?P<filename>[^/]+)/$', TaskUploadView.as_view(), name='upload'),
    url('^suspend/(?P<pk>[0-9]{,10})/', SuspendScheduleView.as_view(), name='suspend'),
    url('^unsuspend/(?P<pk>[0-9]{,10})/', SuspendScheduleView.as_view(), name='unsuspend'),
    url('', include(router.urls), name='tasks')
]
