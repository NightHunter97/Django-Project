from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.accounts.mixins import AdminLogMixin
from apps.reports import forms
from apps.reports.models import Report, Logo
from apps.utils.mixins import AwsUrlMixin


@admin.register(Report)
class ReportAdmin(AdminLogMixin, AwsUrlMixin, admin.ModelAdmin):
    icon = '<i class="material-icons">folder_shared</i>'
    fields = ('title', 'file', 'report_en', 'report_nl', 'report_fr', 'type', 'creator')
    list_display = ('title', 'file', 'report_en_file', 'report_fr_file', 'report_nl_file', 'type', 'creator')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('file', 'creator')

    def has_add_permission(self, request):
        return False

    def report_en_file(self, obj):
        return mark_safe(f'<a href="{self._get_aws_url(obj.report_en)}">{obj.report_en}</a>')

    def report_fr_file(self, obj):
        return mark_safe(f'<a href="{self._get_aws_url(obj.report_fr)}">{obj.report_fr}</a>')

    def report_nl_file(self, obj):
        return mark_safe(f'<a href="{self._get_aws_url(obj.report_nl)}">{obj.report_nl}</a>')


@admin.register(Logo)
class LogoAdmin(AdminLogMixin, AwsUrlMixin, admin.ModelAdmin):
    icon = '<i class="material-icons">image</i>'
    list_display = ('logo',)
    form = forms.LogoForm

    def logo(self, obj):
        return mark_safe(f'<a href="{self._get_aws_url(obj.image)}">{obj.image}</a>')
