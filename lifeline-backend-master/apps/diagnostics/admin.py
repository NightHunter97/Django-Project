from django.contrib import admin
from django.utils.safestring import mark_safe
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from apps.accounts.mixins import AdminLogMixin
from apps.diagnostics.models import DiagnosticFile, Diagnose, HealthScreening, Diagnostic
from apps.utils.mixins import AwsUrlMixin


@admin.register(DiagnosticFile)
class DiagnosticFileAdmin(AdminLogMixin, AwsUrlMixin, admin.ModelAdmin):
    icon = '<i class="material-icons">attachment</i>'
    list_display = ('label', 'uploaded_file', 'is_uploaded')
    readonly_fields = ('label', 'errors', 'is_uploaded')
    fields = ('file', 'label', 'is_uploaded', 'errors')
    change_form_template = 'diagnostics/change_form_template.html'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def uploaded_file(self, obj):
        return mark_safe(f'<a href="{self._get_aws_url(obj.file)}">{obj.file}</a>')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        file = self.get_object(request, object_id).file
        if file:
            extra_context['file_url'] = self._get_aws_url(file)
            extra_context['token'] = jwt_encode_handler(jwt_payload_handler(request.user))
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


@admin.register(Diagnose)
class DiagnoseAdmin(admin.ModelAdmin):
    fields = ('concept_id', 'term_en', 'term_fr', 'term_nl')
    icon = '<i class="material-icons">alarm_add</i>'
    list_display = ('term_en', 'term_fr', 'term_nl')
    search_fields = ('term',)


@admin.register(HealthScreening)
class HealthScreeningAdmin(admin.ModelAdmin):
    icon = '<i class="material-icons">subtitles</i>'
    fields = ('term_en', 'term_fr', 'term_nl')
    list_display = ('term_en', 'term_fr', 'term_nl')


@admin.register(Diagnostic)
class DiagnosticAdmin(AdminLogMixin, admin.ModelAdmin):
    readonly_fields = ('diagnose',)
    fields = ('description', 'user', 'type', 'is_allergy', 'file', 'screening', 'diagnose')
    icon = '<i class="material-icons">search</i>'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('diagnose', 'screening')
