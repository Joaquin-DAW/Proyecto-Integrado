"""
Modelo de ausencias.

La ausencia apunta a una entrada concreta del horario, no solo al profesor. Asi
queda claro que clase, grupo y tramo se han quedado sin cubrir cuando se genera
el parte.
"""
from django.db import models
from apps.schedules.models import HorarioEntry


class Ausencia(models.Model):
    """
    Registro de una falta en una fecha y tramo concreto.

    El campo justificada lo cambia direccion desde la API; el modelo solo guarda
    el estado final.
    """

    fecha = models.DateField()
    descripcion = models.TextField(blank=True, default='')
    tareas = models.TextField(blank=True, default='')
    justificada = models.BooleanField(default=False)
    horario_entry = models.ForeignKey(
        HorarioEntry,
        on_delete=models.CASCADE,
        related_name='ausencias',
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ausencia'
        verbose_name_plural = 'Ausencias'
        ordering = ['-fecha', 'horario_entry__hora']
        # Evita registrar dos veces la misma ausencia para el mismo tramo.
        unique_together = [('fecha', 'horario_entry')]

    def __str__(self):
        estado = 'J' if self.justificada else 'NJ'
        return (
            f"{self.horario_entry.profesor.nombre} | "
            f"{self.fecha} T{self.horario_entry.hora} [{estado}]"
        )

    @property
    def profesor(self):
        return self.horario_entry.profesor

    @property
    def dia_semana(self):
        """Codigo de dia que usa el horario importado: L, M, X, J o V."""
        DIAS = {0: 'L', 1: 'M', 2: 'X', 3: 'J', 4: 'V'}
        return DIAS.get(self.fecha.weekday())
