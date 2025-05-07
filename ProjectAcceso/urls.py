# d:\ruta_a_tu_nuevo_proyecto\proyecto_firmas\proyecto_firmas\urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
# Importa tu vista de login personalizada
from users_app.views import login_view as users_custom_login_view

# Vista simple para redirigir usuarios
from django.shortcuts import redirect
def root_redirect_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff: # O is_superuser
            return redirect('admin:index') # Admin va al panel de admin
        # Corregir el namespace para la redirección
        return redirect('appacceso:home') # Otros usuarios a la pantalla de captura
    return redirect('login') # Si no está autenticado, al login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('appacceso.urls', namespace='appacceso')), # URLs de tu app de captura, corregir namespace

    # Autenticación
    path('accounts/login/', users_custom_login_view, name='login'), # Usa tu vista de login personalizada
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'), # Redirige a login después de logout

    # Redirección desde la raíz y después del login
    path('', root_redirect_view, name='root_redirect'),
]

# Servir archivos de media (firmas subidas) durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
