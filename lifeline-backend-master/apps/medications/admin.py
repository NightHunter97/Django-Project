from django.contrib import admin
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from apps.accounts.mixins import AdminLogMixin
from apps.medications.models import MedicationCategory, Prescription, PrescriptionLog, Drug


class PrescriptionLogAdmin(admin.TabularInline):
    icon = '<i class="material-icons">subtitles</i>'
    model = PrescriptionLog
    extra = 0
    readonly_fields = ('actions', 'created', 'editor', )


@admin.register(MedicationCategory)
class CategoryAdmin(admin.ModelAdmin):
    change_list_template = 'medications/change_list_template.html'
    icon = '<i class="material-icons">event_note</i>'
    search_fields = ('term',)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['token'] = jwt_encode_handler(jwt_payload_handler(request.user))
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Prescription)
class PrescriptionAdmin(AdminLogMixin, admin.ModelAdmin):
    icon = '<i class="material-icons">alarm_add</i>'
    list_display = ('creator', 'editor', 'is_active', 'drug')
    search_fields = ('creator', 'editor')
    inlines = [PrescriptionLogAdmin]

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    icon = '<i class="material-icons">alarm_add</i>'
    list_display = ('name', )
    search_fields = ('name', )
