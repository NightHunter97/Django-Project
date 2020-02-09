from django.contrib import admin

from apps.units.models import Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    icon = '<i class="material-icons">hotel</i>'
    list_display = ('name', 'beds')
