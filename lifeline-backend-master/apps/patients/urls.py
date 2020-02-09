from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from apps.patients.views import PatientsViewSet, PatientMetaView, FilesViewSet, ArchiveCommentViewSet, \
    EmergencyContactViewSet, PatientUploadView, PatientStatusView, IsArchiveCommentRequired, PatientExportView

router = DefaultRouter()
router.register('files', FilesViewSet)
router.register('comments', ArchiveCommentViewSet)
router.register('status', PatientStatusView)
router.register('emergency', EmergencyContactViewSet)
router.register('', PatientsViewSet)


urlpatterns = [
    url('meta/', PatientMetaView.as_view(), name='meta'),
    url('upload/(?P<filename>[^/]+)/$', PatientUploadView.as_view(), name='upload'),
    url(r'export/$', PatientExportView.as_view(), name='export'),
    url('commented/(?P<file_id>[^/]+)/$', IsArchiveCommentRequired.as_view(), name='commented'),
    url('', include(router.urls), name='patients')
]
