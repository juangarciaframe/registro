# d:\AAA_Framework_Acceso\ProjectAcceso\appacceso\admin.py
from django.contrib import admin
from .models import RegistroFirma, Sede
from django.utils.html import format_html
from import_export import resources
from semantic_admin.contrib.import_export.admin import SemanticImportExportModelAdmin
from django.http import HttpResponse
from django.utils import timezone # Para el nombre del archivo y la conversión de zona horaria
from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
from openpyxl.utils import get_column_letter
import openpyxl.styles # Para estilos de celda como negrita
from io import BytesIO
from PIL import Image as PillowImage # Para abrir y manipular la imagen, Pillow es una dependencia de ImageField
import os # Para verificar si el archivo de imagen existe


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'ciudad', 'telefono')
    search_fields = ('nombre', 'ciudad')
    list_filter = ('ciudad',)

class RegistroFirmaResource(resources.ModelResource):
    usuario_username = resources.Field(attribute='usuario__username', column_name='Usuario')
    sede_nombre = resources.Field(attribute='sede__nombre', column_name='Sede')
    fecha_ingreso_formateada = resources.Field(attribute='fecha_ingreso', column_name='Fecha de Ingreso')
    fecha_grabacion_formateada = resources.Field(attribute='fecha_grabacion', column_name='Fecha de Grabación')
    firma_url = resources.Field(column_name='URL Firma')

    class Meta:
        model = RegistroFirma
        fields = ('id', 'usuario_username', 'sede_nombre', 'fecha_ingreso_formateada', 'fecha_grabacion_formateada', 'firma_url')
        export_order = fields

    def dehydrate_fecha_ingreso_formateada(self, registro):
        if registro.fecha_ingreso:
            # Convertir a la zona horaria local antes de formatear
            local_dt = timezone.localtime(registro.fecha_ingreso)
            return local_dt.strftime("%Y-%m-%d %H:%M:%S")
        return ''
    
    def dehydrate_fecha_grabacion_formateada(self, registro):
        if registro.fecha_grabacion:
            # Convertir a la zona horaria local antes de formatear
            local_dt = timezone.localtime(registro.fecha_grabacion)
            return local_dt.strftime("%Y-%m-%d %H:%M:%S")
        return ''
    
    def dehydrate_firma_url(self, registro):
        if registro.firma and hasattr(registro.firma, 'url'):
            # Construir URL absoluta si el request está disponible
            if hasattr(self, 'request') and self.request:
                 return self.request.build_absolute_uri(registro.firma.url)
            return registro.firma.url # Fallback a URL relativa
        return ''

    def before_export(self, queryset, *args, **kwargs):
        # Almacenar el request para usarlo en dehydrate_firma_url
        self.request = kwargs.pop('request', None)
        super().before_export(queryset, *args, **kwargs)

@admin.register(RegistroFirma)
class RegistroFirmaAdmin(SemanticImportExportModelAdmin):
    resource_classes = [RegistroFirmaResource]
    list_display = ('usuario', 'sede', 'fecha_ingreso', 'fecha_grabacion', 'ver_firma')
    list_filter = ('fecha_ingreso', 'usuario', 'sede')
    search_fields = ('usuario__username', 'sede__nombre')
    # 'fecha_ingreso' es editable en el form de captura, pero puede ser readonly en el admin.
    readonly_fields = ('usuario', 'fecha_ingreso', 'fecha_grabacion', 'firma_preview')
    
    fieldsets = (
        (None, {
            'fields': ('usuario', 'sede', 'fecha_ingreso', 'firma_preview', 'fecha_grabacion')
        }),
    )

    def ver_firma(self, obj):
        if obj.firma and hasattr(obj.firma, 'url'):
            return format_html('<a href="{}" target="_blank"><img src="{}" width="100" height="50" style="object-fit: contain;" /></a>', obj.firma.url, obj.firma.url)
        return "Sin firma"
    ver_firma.short_description = 'Firma (Click para ampliar)'

    def firma_preview(self, obj):
        if obj.firma and hasattr(obj.firma, 'url'):
            return format_html('<img src="{}" width="300" height="150" style="object-fit: contain;" />', obj.firma.url)
        return "No hay firma adjunta."
    firma_preview.short_description = 'Vista Previa Firma'

    def export_selected_to_excel_with_images(self, request, queryset):
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        filename = f"registros_firmas_con_imagenes_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"' # Comillas alrededor del filename

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Registros de Firmas'

        headers = ['ID', 'Usuario', 'Sede', 'Fecha de Ingreso', 'Fecha de Grabación', 'Firma']
        for col_num, header_title in enumerate(headers, 1):
            cell = sheet.cell(row=1, column=col_num, value=header_title)
            cell.font = openpyxl.styles.Font(bold=True)

        row_num = 2
        img_display_height_px = 80
        row_height_pt = (img_display_height_px * 0.75) + 15 
        img_max_width_px = 200
        firma_col_width = (img_max_width_px / 7) + 2

        for registro in queryset:
            sheet.cell(row=row_num, column=1, value=registro.id)
            sheet.cell(row=row_num, column=2, value=registro.usuario.username)
            sheet.cell(row=row_num, column=3, value=registro.sede.nombre if registro.sede else 'N/A')
            
            fecha_ingreso_str = ''
            if registro.fecha_ingreso:
                # Convertir a la zona horaria local antes de formatear
                fecha_ingreso_str = timezone.localtime(registro.fecha_ingreso).strftime("%Y-%m-%d %H:%M:%S")
            sheet.cell(row=row_num, column=4, value=fecha_ingreso_str)
            
            fecha_grabacion_str = ''
            if registro.fecha_grabacion:
                # Convertir a la zona horaria local antes de formatear
                fecha_grabacion_str = timezone.localtime(registro.fecha_grabacion).strftime("%Y-%m-%d %H:%M:%S")
            sheet.cell(row=row_num, column=5, value=fecha_grabacion_str)

            firma_cell_anchor = f'{get_column_letter(6)}{row_num}'
            sheet.row_dimensions[row_num].height = row_height_pt

            if registro.firma and hasattr(registro.firma, 'path') and registro.firma.path and os.path.exists(registro.firma.path):
                try:
                    img_pil = PillowImage.open(registro.firma.path)
                    original_width, original_height = img_pil.size
                    
                    if original_height == 0:
                        sheet.cell(row=row_num, column=6, value="Error: Altura de imagen cero")
                        row_num +=1
                        continue

                    aspect_ratio = original_width / original_height
                    current_img_width_px = int(img_display_height_px * aspect_ratio)
                    current_img_height_px = img_display_height_px

                    if current_img_width_px > img_max_width_px:
                        current_img_width_px = img_max_width_px
                        current_img_height_px = int(current_img_width_px / aspect_ratio) if aspect_ratio != 0 else img_display_height_px

                    img_openpyxl = OpenpyxlImage(registro.firma.path)
                    img_openpyxl.height = current_img_height_px
                    img_openpyxl.width = current_img_width_px
                    
                    sheet.add_image(img_openpyxl, firma_cell_anchor)
                except FileNotFoundError:
                    sheet.cell(row=row_num, column=6, value="Archivo no encontrado")
                except Exception as e:
                    sheet.cell(row=row_num, column=6, value=f"Error al cargar imagen: {e}")
            else:
                sheet.cell(row=row_num, column=6, value="Sin firma o ruta inválida")
            
            row_num += 1

        for i, column_cells in enumerate(sheet.columns):
            col_letter = get_column_letter(i + 1)
            if col_letter == get_column_letter(6):
                sheet.column_dimensions[col_letter].width = firma_col_width
                continue
            
            max_length = 0
            for cell in column_cells:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            sheet.column_dimensions[col_letter].width = max_length + 2
        
        workbook.save(response)
        return response

    export_selected_to_excel_with_images.short_description = "Exportar seleccionados a Excel (con imágenes)"

    actions = [export_selected_to_excel_with_images]

    def get_export_resource_kwargs(self, request, *args, **kwargs):
        # Pasar el request al Resource para construir URLs absolutas
        return {"request": request}
