from django.contrib import admin
from .models import ParteAusencias


@admin.register(ParteAusencias)
class ParteAusenciasAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'generado_en', 'pdf_file')
    list_filter = ('tipo', 'fecha')
    date_hierarchy = 'fecha'
