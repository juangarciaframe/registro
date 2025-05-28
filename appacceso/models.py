# d:\ruta_a_tu_nuevo_proyecto\proyecto_firmas\captura\models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Sede(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Sede")
    direccion = models.CharField(max_length=200, verbose_name="Dirección")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")

    # Puedes añadir más campos si los necesitas, como dirección, ciudad, etc.

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Sede"
        verbose_name_plural = "Sedes"
        ordering = ['nombre']

class RegistroFirma(models.Model):
    TIPO_REGISTRO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('salida', 'Salida'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    sede = models.ForeignKey(Sede, on_delete=models.PROTECT, verbose_name="Sede", null=True, blank=False) # null=True temporalmente para migraciones si hay datos existentes
    tipo_registro = models.CharField(
        max_length=10,
        choices=TIPO_REGISTRO_CHOICES,
        default='ingreso',
        verbose_name="Tipo de Registro"
    )
    fecha_ingreso = models.DateTimeField(default=timezone.now, verbose_name="Fecha") # Cambiado verbose_name
    firma = models.ImageField(upload_to='firmas/%Y/%m/%d/', verbose_name="Firma Digital")
    fecha_grabacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Grabación (Automática)")

    def __str__(self):
        return f"{self.get_tipo_registro_display()} de {self.usuario.username} en {self.sede.nombre if self.sede else 'Sede no especificada'} - {self.fecha_ingreso.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Registro de Firma"
        verbose_name_plural = "Registros de Firmas"
        ordering = ['-fecha_ingreso']
