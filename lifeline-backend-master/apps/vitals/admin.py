from django.contrib import admin

from apps.accounts.mixins import AdminLogMixin
from apps.vitals.models import VitalsParam


@admin.register(VitalsParam)
class VitalsAdmin(AdminLogMixin, admin.ModelAdmin):
    icon = '<i class="material-icons">control_point</i>'
    list_display = ('file', 'type', 'value', 'user', 'created', 'comment')
    search_fields = ('file__file_id', )
    list_filter = ('type', )
