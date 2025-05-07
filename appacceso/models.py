# d:\ruta_a_tu_nuevo_proyecto\proyecto_firmas\captura\models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class RegistroFirma(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    fecha_ingreso = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Ingreso (Editable)")
    comentarios = models.TextField(verbose_name="Comentarios", blank=True, null=True)
    firma = models.ImageField(upload_to='firmas/%Y/%m/%d/', verbose_name="Firma Digital")
    fecha_grabacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Grabación (Automática)")

    def __str__(self):
        return f"Registro de {self.usuario.username} - {self.fecha_ingreso.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Registro de Firma"
        verbose_name_plural = "Registros de Firmas"
        ordering = ['-fecha_ingreso']
