# d:\AAA_Framework_Acceso\ProjectAcceso\appacceso\admin.py
from django.contrib import admin
from .models import RegistroFirma, Sede
from django.utils.html import format_html
from import_export import resources
from semantic_admin.contrib.import_export.admin import SemanticImportExportModelAdmin
from django.http import HttpResponse
from django.utils import timezone # Para el nombre del archivo
from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenpyxlImage # Renombrar para evitar conflicto con PIL.Image
import openpyxl.utils # Para get_column_letter


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'ciudad', 'telefono')
    search_fields = ('nombre', 'ciudad')
    list_filter = ('ciudad',)

class RegistroFirmaResource(resources.ModelResource):
    # Personalizar los campos y cómo se exportan
    usuario_username = resources.Field(attribute='usuario__username', column_name='Usuario')
    sede_nombre = resources.Field(attribute='sede__nombre', column_name='Sede')
    fecha_ingreso_formateada = resources.Field(attribute='fecha_ingreso', column_name='Fecha de Ingreso')
    fecha_grabacion_formateada = resources.Field(attribute='fecha_grabacion', column_name='Fecha de Grabación')
    # Si quieres exportar la URL de la firma (ten en cuenta que esto es solo la URL, no la imagen en sí)
    # firma_url = resources.Field(attribute='firma__url', column_name='URL Firma')


    class Meta:
        model = RegistroFirma
        # Define los campos que quieres exportar y su orden
        fields = ('id', 'usuario_username', 'sede_nombre', 'fecha_ingreso_formateada', 'fecha_grabacion_formateada')
        # Si quieres incluir la URL de la firma, añade 'firma_url' a fields
        # fields = ('id', 'usuario_username', 'sede_nombre', 'fecha_ingreso_formateada', 'fecha_grabacion_formateada', 'firma_url')
        export_order = fields # Mantiene el orden definido en fields

    def dehydrate_fecha_ingreso_formateada(self, registro):
        return registro.fecha_ingreso.strftime("%Y-%m-%d %H:%M:%S") if registro.fecha_ingreso else ''

    def dehydrate_fecha_grabacion_formateada(self, registro):
        return registro.fecha_grabacion.strftime("%Y-%m-%d %H:%M:%S") if registro.fecha_grabacion else ''
    
    # Si decides exportar la URL de la firma:
    # def dehydrate_firma_url(self, registro):
    #     return registro.firma.url if registro.firma else ''





@admin.register(RegistroFirma)
class RegistroFirmaAdmin(SemanticImportExportModelAdmin): # Cambiar la herencia a la de django-import-export
    # Forzar el uso de nuestra plantilla sobrescrita
    resource_classes = [RegistroFirmaResource] # Usar la clase Resource
    list_display = ('usuario', 'sede', 'fecha_ingreso', 'fecha_grabacion', 'ver_firma')
    list_filter = ('fecha_ingreso', 'usuario', 'sede')
    search_fields = ('usuario__username', 'sede__nombre')
    # Hacemos 'sede' editable en el form de admin si no es readonly
    readonly_fields = ('usuario', 'fecha_ingreso', 'fecha_grabacion', 'firma_preview')
    # Si quieres que 'sede' sea editable en el admin, quítalo de readonly_fields.
    # Si 'sede' es null=True en el modelo y quieres que sea opcional en el admin, está bien.
    # Si 'sede' es null=False, debe ser un campo requerido.

    fieldsets = (
        (None, {
            'fields': ('usuario', 'sede', 'fecha_ingreso', 'firma_preview', 'fecha_grabacion')
        }),
    )
    # La acción de exportar se añade automáticamente por ImportExportModelAdmin

    def ver_firma(self, obj):
        if obj.firma:
            return format_html('<a href="{}" target="_blank"><img src="{}" width="100" height="50" style="object-fit: contain;" /></a>', obj.firma.url, obj.firma.url)
        return "Sin firma"
    ver_firma.short_description = 'Firma (Click para ampliar)'

    def firma_preview(self, obj): # Para el form de admin
        if obj.firma:
            return format_html('<img src="{}" width="300" height="150" style="object-fit: contain;" />', obj.firma.url)
        return "No hay firma adjunta."
    firma_preview.short_description = 'Vista Previa Firma'
