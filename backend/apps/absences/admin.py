from django.contrib import admin
from .models import Ausencia


@admin.register(Ausencia)
class AusenciaAdmin(admin.ModelAdmin):
    list_display = ('profesor', 'fecha', 'hora_tramo', 'justificada', 'descripcion')
    list_filter = ('justificada', 'fecha')
    search_fields = ('horario_entry__profesor__nombre',)
    date_hierarchy = 'fecha'

    def profesor(self, obj):
        return obj.horario_entry.profesor.nombre
    profesor.short_description = 'Profesor'

    def hora_tramo(self, obj):
        return f"T{obj.horario_entry.hora}"
    hora_tramo.short_description = 'Tramo'
