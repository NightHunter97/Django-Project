from django.contrib import admin
from rest_framework_jwt.serializers import jwt_payload_handler
from rest_framework_jwt.utils import jwt_encode_handler

from apps.accounts.mixins import AdminLogMixin
from apps.tasks.forms import AddGroupCategoryForm
from apps.tasks.models import Task, Category, Schedule


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    icon = '<i class="material-icons">alarm_add</i>'
    list_display = ('name_en', 'name_fr', 'name_nl', 'category')
    fields = ('name_en', 'name_fr', 'name_nl', 'category')
    search_fields = ('name_en', 'name_fr', 'name_nl')
    list_filter = ('category',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = AddGroupCategoryForm
    icon = '<i class="material-icons">schedule</i>'
    list_display = ('slug', 'name_en', 'name_fr', 'name_nl')
    fields = ('name_en', 'name_fr', 'name_nl', 'icon', 'image', 'groups')
    search_fields = ('name_en', 'name_fr', 'name_nl')
    change_form_template = 'tasks/change_form.html'

    class Media:
        js = ('tasks/js/category.js', )

    inlines = [TaskInline]

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['token'] = jwt_encode_handler(jwt_payload_handler(request.user))
        return super().changeform_view(request, object_id=object_id, form_url=form_url, extra_context=extra_context)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.slug == 'medication':
            return False
        return True


@admin.register(Schedule)
class ScheduleAdmin(AdminLogMixin, admin.ModelAdmin):
    icon = '<i class="material-icons">alarm</i>'
    list_display = ('date', 'time', 'task', 'status', 'root_id')
    list_filter = ('date', 'status')
    search_fields = ('date', 'task__name', 'root_id')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('task')
