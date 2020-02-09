from django.contrib import admin

from apps.wish.models import HL7System


@admin.register(HL7System)
class HL7SystemAdmin(admin.ModelAdmin):
    list_display = ('user', 'os', 'created')
