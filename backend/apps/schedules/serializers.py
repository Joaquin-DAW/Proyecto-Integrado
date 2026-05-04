from rest_framework import serializers
from .models import HorarioEntry


class HorarioEntrySerializer(serializers.ModelSerializer):
    profesor_nombre = serializers.CharField(source='profesor.nombre', read_only=True)
    profesor_id = serializers.IntegerField(source='profesor.id', read_only=True)
    dia_display = serializers.CharField(source='get_dia_display', read_only=True)
    es_guardia = serializers.BooleanField(read_only=True)
    es_recreo = serializers.BooleanField(read_only=True)

    class Meta:
        model = HorarioEntry
        fields = (
            'id', 'asignatura', 'curso', 'aula',
            'profesor_id', 'profesor_nombre', 'dia', 'dia_display', 'hora',
            'es_guardia', 'es_recreo',
        )


class HorarioImportSerializer(serializers.Serializer):
    """
    Entrada para importar horarios.

    El caso normal desde Angular es multipart, pero se acepta base64 para poder
    probar la API o reutilizar integraciones mas simples.
    """
    fichero = serializers.FileField(required=False)
    fichero_base64 = serializers.CharField(required=False)

    def validate(self, data):
        if not data.get('fichero') and not data.get('fichero_base64'):
            raise serializers.ValidationError(
                "Debes enviar el fichero como 'fichero' (multipart) o 'fichero_base64' (base64)."
            )
        return data
