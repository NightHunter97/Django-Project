from django.contrib import admin

from apps.accounts.mixins import AdminLogMixin
from apps.journal.models import Journal


@admin.register(Journal)
class JournalAdmin(AdminLogMixin, admin.ModelAdmin):
    icon = '<i class="material-icons">local_library</i>'
    list_display = ('name', 'user', 'file', 'type', 'tag')
    list_filter = ('type', 'tag')
    search_fields = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'file')
