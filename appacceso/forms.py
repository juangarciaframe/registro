# d:\ruta_a_tu_nuevo_proyecto\proyecto_firmas\captura\forms.py
from django import forms
from .models import RegistroFirma

class RegistroFirmaForm(forms.ModelForm):
    # Campo oculto para recibir los datos de la firma en base64 desde el JS
    signature_data_url = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = RegistroFirma
        fields = ['fecha_ingreso', 'comentarios', 'signature_data_url'] # usuario se maneja en la vista
        widgets = {
            'comentarios': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Añade tus comentarios aquí...'}),
            'fecha_ingreso': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
        labels = {
            'fecha_ingreso': 'Fecha y Hora de Ingreso',
        }
