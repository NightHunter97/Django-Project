from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from apps.documents.views import DocumentTypeListView, DocumentsView, DownloadView, PreviewView


router = DefaultRouter()
router.register('', DocumentsView)


urlpatterns = [
    url('document_types/', DocumentTypeListView.as_view(), name='document_type'),
    url('preview/', PreviewView.as_view(), name='view_pdf'),
    url('', include(router.urls), name='documents'),
    url('download/(?P<pk>\d+)$', DownloadView.as_view(), name='download_pdf'),
]
