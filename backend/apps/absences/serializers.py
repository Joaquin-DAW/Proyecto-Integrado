from rest_framework import serializers
from .models import Ausencia
from apps.schedules.models import HorarioEntry


class AusenciaSerializer(serializers.ModelSerializer):
    """Ausencia lista para pintar en tablas, con datos del horario ya resueltos."""

    profesor_nombre = serializers.CharField(
        source='horario_entry.profesor.nombre', read_only=True
    )
    asignatura = serializers.CharField(source='horario_entry.asignatura', read_only=True)
    curso = serializers.CharField(source='horario_entry.curso', read_only=True)
    aula = serializers.CharField(source='horario_entry.aula', read_only=True)
    hora = serializers.IntegerField(source='horario_entry.hora', read_only=True)
    dia = serializers.CharField(source='horario_entry.dia', read_only=True)

    class Meta:
        model = Ausencia
        fields = (
            'id', 'fecha', 'descripcion', 'tareas', 'justificada', 'creada_en',
            'horario_entry', 'profesor_nombre', 'asignatura', 'curso', 'aula', 'hora', 'dia',
        )
        read_only_fields = ('id', 'creada_en', 'justificada')


class CreateAusenciaSerializer(serializers.Serializer):
    """
    Datos de alta de ausencias.

    horas permite marcar varios tramos en una sola peticion, que es lo normal si
    un profesor falta varias clases el mismo dia.

    Ejemplo de payload:
      {
        "fecha": "2026-04-23",
        "horas": [1, 2, 3],
        "descripcion": "Baja médica",
        "tareas": "Ejercicios 1 y 2 de la pagina 45",
        "profesor_id": 5   ← solo si lo envía el Equipo Directivo
      }
    """
    fecha = serializers.DateField()
    horas = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=14),
        min_length=1,
    )
    descripcion = serializers.CharField(required=False, default='', allow_blank=True)
    tareas = serializers.CharField(required=False, default='', allow_blank=True)
    profesor_id = serializers.IntegerField(required=False)

    def validate_horas(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("No puedes repetir el mismo tramo.")
        return value


class JustificarAusenciaSerializer(serializers.Serializer):
    """Cuerpo minimo para cambiar el estado de justificacion."""
    justificada = serializers.BooleanField()
