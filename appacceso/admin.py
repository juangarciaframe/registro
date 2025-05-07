# d:\ruta_a_tu_nuevo_proyecto\proyecto_firmas\captura\admin.py
from django.contrib import admin
from .models import RegistroFirma
from django.utils.html import format_html

@admin.register(RegistroFirma)
class RegistroFirmaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_ingreso', 'fecha_grabacion', 'comentarios_resumen', 'ver_firma')
    list_filter = ('fecha_ingreso', 'usuario')
    search_fields = ('usuario__username', 'comentarios')
    readonly_fields = ('usuario', 'fecha_ingreso', 'fecha_grabacion', 'firma_preview') # Para ver en el detalle

    def comentarios_resumen(self, obj):
        return (obj.comentarios[:75] + '...') if obj.comentarios and len(obj.comentarios) > 75 else obj.comentarios
    comentarios_resumen.short_description = 'Comentarios'

    def ver_firma(self, obj):
        if obj.firma:
            return format_html('<a href="{}" target="_blank"><img src="{}" width="150" /></a>', obj.firma.url, obj.firma.url)
        return "Sin firma"
    ver_firma.short_description = 'Firma (Click para ampliar)'

    def firma_preview(self, obj): # Para el form de admin
        if obj.firma:
            return format_html('<img src="{}" width="300" />', obj.firma.url)
        return "No hay firma adjunta."
    firma_preview.short_description = 'Vista Previa Firma'
