from django.contrib import admin
from .models import HorarioEntry


@admin.register(HorarioEntry)
class HorarioEntryAdmin(admin.ModelAdmin):
    list_display = ('profesor', 'dia', 'hora', 'asignatura', 'curso', 'aula')
    list_filter = ('dia', 'hora', 'profesor')
    search_fields = ('profesor__nombre', 'asignatura', 'curso')
    ordering = ('dia', 'hora')
