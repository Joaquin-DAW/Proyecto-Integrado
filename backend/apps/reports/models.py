"""
Partes de ausencias generados por el sistema.

Cada parte corresponde a una fecha y a un modulo del centro. El PDF se guarda
en media para poder descargarlo o enviarlo despues sin tener que recalcularlo.
"""
from django.db import models


class ParteAusencias(models.Model):
    """
    Registro del PDF generado.

    FileField guarda la ruta relativa dentro de MEDIA_ROOT y Django se encarga
    de abrirlo cuando se descarga desde la API.
    """

    MODULO_A = 'A'
    MODULO_B = 'B'

    TIPO_CHOICES = [
        (MODULO_A, 'Módulo A'),
        (MODULO_B, 'Módulo B'),
    ]

    fecha = models.DateField()
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    generado_en = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='partes/%Y/%m/', blank=True, null=True)

    class Meta:
        verbose_name = 'Parte de ausencias'
        verbose_name_plural = 'Partes de ausencias'
        ordering = ['-fecha', 'tipo']
        unique_together = [('fecha', 'tipo')]

    def __str__(self):
        return f"Parte {self.get_tipo_display()} — {self.fecha}"
