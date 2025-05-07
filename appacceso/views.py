# d:\ruta_a_tu_nuevo_proyecto\proyecto_firmas\captura\views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import RegistroFirmaForm
from .models import RegistroFirma
import base64
from django.core.files.base import ContentFile
import uuid # Para nombres de archivo únicos

@login_required
def pantalla_captura_view(request):
    if request.method == 'POST':
        form = RegistroFirmaForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.usuario = request.user
            # fecha_ingreso ahora viene del formulario y es editable.
            # fecha_grabacion se establecerá automáticamente por auto_now_add=True en el modelo.

            signature_base64 = form.cleaned_data.get('signature_data_url')
            if signature_base64:
                try:
                    # El formato es "data:image/png;base64,iVBORw0KGgo..."
                    format, imgstr = signature_base64.split(';base64,')
                    ext = format.split('/')[-1]  # ej: "png"
                    # Generar un nombre de archivo único
                    filename = f"firma_{uuid.uuid4()}.{ext}"
                    data = ContentFile(base64.b64decode(imgstr), name=filename)
                    registro.firma = data
                except Exception as e:
                    messages.error(request, f"Error al procesar la firma: {e}")
                    return render(request, 'captura/pantalla_captura.html', {'form': form})
            else:
                # Si la firma es opcional y no se proveyó, no hagas nada.
                # Si es requerida, deberías añadir un error al form:
                # form.add_error('signature_data_url', 'La firma es requerida.')
                # return render(request, 'captura/pantalla_captura.html', {'form': form})
                pass # Asumiendo que la firma puede ser opcional o validada en JS

            registro.save()
            messages.success(request, 'Registro guardado exitosamente.')
            return redirect('appacceso:pantalla_captura') # Redirige a la misma página para nueva captura
            # O a una página de éxito: return redirect('captura:captura_exitosa')
    else:
        form = RegistroFirmaForm()
        # El default=timezone.now en el modelo RegistroFirma.fecha_ingreso
        # se encargará de pre-rellenar el campo en el formulario para nuevos registros.

    context = {
        'form': form,
    }
    return render(request, 'captura/pantalla_captura.html', context)

# Opcional: una vista para una página de "éxito"
# @login_required
# def captura_exitosa_view(request):
#    return render(request, 'captura/captura_exitosa.html')
