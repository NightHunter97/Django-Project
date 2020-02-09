import base64

from django.contrib import admin
from django.core.cache import cache
from django.utils.safestring import mark_safe

from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from apps.accounts.mixins import AdminLogMixin
from apps.patients.forms import PatientForm
from apps.patients.models import Patient, File, EmergencyContact, ArchiveComment


class FileInline(admin.TabularInline):
    readonly_fields = ('closed_since', 'open_tasks', 'due_tasks')
    model = File
    extra = 0


class EmergencyContactsInline(admin.TabularInline):
    model = EmergencyContact
    extra = 0


@admin.register(Patient)
class PatentAdmin(AdminLogMixin, admin.ModelAdmin):
    export_pdf_format = 'export_pdf_patient_{}'

    icon = '<i class="material-icons">contacts</i>'
    list_display = ('patient_id', 'full_name', 'national_register', 'created', 'export_pdf')
    form = PatientForm

    readonly_fields = ('patient_id', 'files', 'created', 'modified', 'is_gdpr_agreed')
    change_list_template = 'patients/change_list_template.html'
    change_form_template = 'patients/change_form_template.html'
    search_fields = ('full_name', 'patient_id')

    fieldsets = (
        ('Patient INFO', {
            'fields': (
                'is_gdpr_agreed', 'patient_id', 'created', 'modified',
                'full_name', 'card_number', 'card_type', 'document_type', 'language', 'birth_date', 'gender',
                'marital_status', 'partner_name', 'nationality', 'country', 'address', 'post_code', 'national_register',
                'foreign_register', 'phone_number', 'email', 'is_vip', 'religion', 'general_practitioner',
                'death_date', 'note'
            )
        }),
        ('Health Insurance INFO', {
            'fields': (
                'insurance_policy', 'policy_holder', 'validity_end', 'beneficiary_id', 'beneficiary_occupation',
                'heading_code', 'is_employed', 'dependants', 'is_third_party_auth', 'disability_recognition',
                'regional_recognition', 'disability_assessment_points', 'income_origin', 'income_amount',
                'expenses'
            ),
        }),
        ('Social INFO', {
            'fields': (
                'debts', 'attorney', 'management', 'admission', 'occupation', 'career', 'education', 'edu_pathway'
            ),
        }),
    )

    inlines = [FileInline, EmergencyContactsInline]

    def export_pdf(self, obj):
        pdf = cache.get(self.export_pdf_format.format(obj.id))
        if pdf:
            if self.is_pdf_generating(pdf):
                return mark_safe(f'<i class="fa fa-refresh fa-spin" title="export {obj.full_name}.pdf"></i>')
            return mark_safe(
                f'<a class="flex" '
                f'href="data:application/pdf;base64, {base64.b64encode(pdf["content"]).decode("utf-8")}" '
                f'download="export {obj.full_name}.pdf" title="export {obj.full_name}.pdf">'
                f'<i class="material-icons green-icon">picture_as_pdf</i></a>'
            )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['token'] = jwt_encode_handler(jwt_payload_handler(request.user))
        return super().changelist_view(request, extra_context=extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['token'] = jwt_encode_handler(jwt_payload_handler(request.user))
        pdf = cache.get(self.export_pdf_format.format(object_id))
        if not pdf:
            extra_context['generate_pdf'] = True
        elif self.is_pdf_generating(pdf):
            extra_context['generating'] = True
        else:
            extra_context['pdf'] = 'data:application/pdf;base64,' + base64.b64encode(pdf['content']).decode("utf-8")
            extra_context['owner'] = pdf['owner']
        return super().changeform_view(
            request=request,
            object_id=object_id,
            form_url=form_url,
            extra_context=extra_context
        )

    @staticmethod
    def is_pdf_generating(pdf):
        return pdf == 'generating'


@admin.register(ArchiveComment)
class ArchiveAdmin(AdminLogMixin, admin.ModelAdmin):
    icon = '<i class="material-icons">archive</i>'
    list_display = ('id', 'comment', 'file', 'user', 'created')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('file', 'user')
