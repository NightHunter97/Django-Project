from django.contrib import admin

from apps.accounts.mixins import AdminLogMixin
from apps.wounds.models import Wound, Evolution


class EvolutionAdmin(admin.TabularInline):
    model = Evolution
    extra = 0
    readonly_fields = ('created', )


@admin.register(Wound)
class WoundAdmin(AdminLogMixin, admin.ModelAdmin):
    icon = '<i class="material-icons">camera</i>'
    list_display = ('name', 'type', 'localization', 'is_cured')
    search_fields = ('name', )
    list_filter = ('type', )
    inlines = [EvolutionAdmin]
