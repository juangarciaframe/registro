# d:\AAA_Framework\ProjectFrameworksas\users_app\views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Asegúrate de que LoginForm esté definido en users_app/forms.py
from .forms import LoginForm
from django.utils.http import url_has_allowed_host_and_scheme
import logging

logger = logging.getLogger(__name__)

# Define el namespace de la app para usar en redirecciones y URLs
app_name = 'users_app'

def login_view(request):
    """
    Vista de login personalizada que maneja la autenticación y la lógica
    de selección de empresa basada en las asignaciones del usuario.
    """
    error_message = None
    # Si el usuario ya está autenticado y accede a /login/, redirigir a home
    if request.user.is_authenticated:
        # Redirigir a una página apropiada, por ejemplo, la pantalla de captura o la raíz.
        return redirect('appacceso:pantalla_captura') # Ajusta 'appacceso:pantalla_captura' si es necesario

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                logger.info(f"Usuario {user.username} autenticado exitosamente.")
                
                # Manejar redirección 'next'
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                else:
                    # Redirección por defecto si no hay 'next' o no es seguro
                    # Ajusta 'appacceso:pantalla_captura' a tu página de destino deseada post-login
                    return redirect('appacceso:pantalla_captura')

            else:
                # Autenticación fallida
                error_message = "Usuario o contraseña incorrectos."
                logger.warning(f"Login: Falló autenticación para {username}")
                print(f"DEBUG (login_view): Falló autenticación para {username}") # DEBUG
        else:
            # Formulario inválido
            error_message = "Por favor, corrija los errores en el formulario."
            logger.warning(f"Login: Formulario inválido recibido.")
            print(f"DEBUG (login_view): Formulario inválido.") # DEBUG

    else: # Método GET
        form = LoginForm()

    # Renderizar la plantilla de login
    # Asegúrate que la ruta 'users_app/login.html' sea correcta
    context = {
        'form': form,
        'error_message': error_message,
        'next': request.GET.get('next', '') # Pasar 'next' a la plantilla
    }
    return render(request, 'users_app/login.html', context)


def logout_view(request):
    """
    Vista para cerrar la sesión del usuario, limpiando la empresa seleccionada.
    """
    user_display = str(request.user) if request.user.is_authenticated else "Usuario anónimo"
    # Limpiar la sesión antes de desloguear
    
    logout(request)
    logger.info(f"Logout: Sesión cerrada para {user_display}")
    print(f"DEBUG (logout_view): Sesión cerrada. Redirigiendo a login.") # DEBUG
    # Redirigir a la página de login principal definida en ProjectAcceso/urls.py
    return redirect('login')
