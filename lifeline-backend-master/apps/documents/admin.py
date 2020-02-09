import uuid
import os

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import DocumentType, Document
from .forms import DocumentForm
from django.utils.safestring import mark_safe
from apps.utils.mixins import AwsUrlMixin


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    icon = '<i class="material-icons">subtitles</i>'
    list_display = ('name', )
    list_display_links = ('name', )

@admin.register(Document)
class DocumentAdmin(AwsUrlMixin, admin.ModelAdmin):
    icon = '<i class="material-icons">attachment</i>'
    form = DocumentForm
    list_display = ('name', 'document_type', 'view_file')
    list_display_links = ('name',)

    def view_file(self, obj):
        return mark_safe(f'<a href="{self._get_aws_url(obj.file, 5)}">{obj.file}</a>')

