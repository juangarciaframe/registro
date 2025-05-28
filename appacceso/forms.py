# d:\ruta_a_tu_nuevo_proyecto\proyecto_firmas\captura\forms.py
from django import forms
from django.utils import timezone
from .models import RegistroFirma

class RegistroFirmaForm(forms.ModelForm):
    # Campo oculto para recibir los datos de la firma en base64 desde el JS
    signature_data_url = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = RegistroFirma
        # Actualizamos los campos: quitamos 'comentarios', añadimos 'sede'
        fields = ['sede', 'tipo_registro', 'fecha_ingreso', 'signature_data_url'] # usuario se maneja en la vista
        widgets = {
            'fecha_ingreso': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'sede': forms.Select(attrs={'class': 'form-select'}), # Para que se vea bien con Bootstrap
            'tipo_registro': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'fecha_ingreso': 'Fecha y Hora', # Cambiada etiqueta
            'sede': 'Sede de Ingreso',
            'tipo_registro': 'Tipo de Registro',
        }

    def clean_fecha_ingreso(self):
        fecha_ingreso = self.cleaned_data.get('fecha_ingreso')
        if fecha_ingreso and timezone.is_naive(fecha_ingreso):
            fecha_ingreso = timezone.make_aware(fecha_ingreso, timezone.get_default_timezone())
        
        if fecha_ingreso and fecha_ingreso > timezone.now():
            raise forms.ValidationError("La fecha de ingreso no puede ser una fecha futura.")
        return fecha_ingreso
