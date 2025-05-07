# d:\ruta_a_tu_nuevo_proyecto\proyecto_firmas\captura\urls.py
from django.urls import include, path
from . import views
from users_app import views as users_app_views # O importa directamente

app_name = 'appacceso' # Namespace para las URLs de esta app



urlpatterns = [
    path('registro/', views.pantalla_captura_view, name='pantalla_captura'),
    path('users/', include('users_app.urls', namespace='users_app')), # Para incluir todas las de users_app

    # path('exito/', views.captura_exitosa_view, name='captura_exitosa'), # Si creas la página de éxito
]
