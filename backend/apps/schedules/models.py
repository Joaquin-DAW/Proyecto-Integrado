"""
Modelo del horario del centro.

El TXT de Séneca/HORW ya trae asignatura, curso y aula como texto, asi que se
guardan directamente en cada entrada. Para este proyecto no compensa crear
tablas aparte de Asignatura, Curso o Aula: se consultan mucho, pero no se editan
como entidades independientes.
"""
from django.db import models
from apps.users.models import Profesor


# Codigos que usa el fichero: dias lectivos y tramos del 1 al 14.

HORA_CHOICES = [(i, f'Tramo {i}') for i in range(1, 15)]

DIA_CHOICES = [
    ('L', 'Lunes'),
    ('M', 'Martes'),
    ('X', 'Miércoles'),
    ('J', 'Jueves'),
    ('V', 'Viernes'),
]

# En estos tramos se trata como recreo; el PDF los pinta distinto.
TRAMOS_RECREO = {4, 11}


class HorarioEntry(models.Model):
    """
    Una linea real del horario: profesor, asignatura, grupo/aula, dia y tramo.

    curso y aula pueden venir vacios, sobre todo en guardias, apoyos o entradas
    especiales del fichero.
    """

    asignatura = models.CharField(max_length=200)
    curso = models.CharField(max_length=100, blank=True, default='')
    aula = models.CharField(max_length=50, blank=True, default='')
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.CASCADE,
        related_name='horario_entries',
    )
    dia = models.CharField(max_length=1, choices=DIA_CHOICES)
    hora = models.PositiveSmallIntegerField(choices=HORA_CHOICES)

    class Meta:
        verbose_name = 'Entrada de horario'
        verbose_name_plural = 'Entradas de horario'
        ordering = ['dia', 'hora', 'profesor__nombre']
        # Solo bloquea duplicados calcados; una misma hora puede tener varios grupos.
        unique_together = [('profesor', 'dia', 'hora', 'asignatura', 'curso', 'aula')]

    def __str__(self):
        return f"{self.profesor.nombre} | {self.get_dia_display()} T{self.hora} | {self.asignatura}"

    @property
    def es_guardia(self):
        return self.asignatura.lower().startswith('guardia')

    @property
    def es_recreo(self):
        return self.hora in TRAMOS_RECREO
