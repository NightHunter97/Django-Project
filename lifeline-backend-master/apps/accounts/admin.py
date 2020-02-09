from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from rest_framework_jwt.utils import jwt_encode_handler, jwt_payload_handler

from apps.accounts.forms import UserAddForm, UserUpdateForm, UserAddPermissionForm
from apps.accounts.models import User
from django.utils.translation import ugettext_lazy as _

from apps.patients.services import get_all_patients

admin.site.unregister(Group)


@admin.register(User)
class AccountAdmin(UserAdmin):
    icon = '<i class="material-icons">person</i>'
    change_form_template = 'accounts/user_change_form.html'
    change_list_template = 'accounts/change_list_template.html'
    add_form = UserAddForm
    form = UserUpdateForm
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'gender', 'phone', 'line', 'inami', 'language')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Units'), {'fields': ('units', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'last_name', 'language', 'phone', 'line', 'inami', 'password1', 'password2', 'groups', 'units'
            ),
        }),
    )
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['patients'] = get_all_patients()
        extra_context['token'] = jwt_encode_handler(jwt_payload_handler(request.user))
        return self.changeform_view(request, object_id, form_url, extra_context)


@admin.register(Group)
class GroupAdmin(GroupAdmin):
    form = UserAddPermissionForm

    def __init__(self, model, admin_site):
        model._meta.app_config.verbose_name = _("Permissions")
        model._meta.verbose_name_plural = _("Roles")
        model._meta.verbose_name = _("Role")
        super().__init__(model, admin_site)
