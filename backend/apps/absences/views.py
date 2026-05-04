import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.models import Profesor
from apps.users.permissions import IsEquipoDireccion, IsEquipoDireccionOrReadOwn
from apps.schedules.models import HorarioEntry, TRAMOS_RECREO
from .models import Ausencia
from .serializers import AusenciaSerializer, CreateAusenciaSerializer, JustificarAusenciaSerializer


def _get_dia_semana(fecha: datetime.date) -> str:
    """Traduce una fecha al codigo que usa el fichero de horarios."""
    DIAS = {0: 'L', 1: 'M', 2: 'X', 3: 'J', 4: 'V'}
    return DIAS.get(fecha.weekday())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_ausencias(request):
    """
    Listado de ausencias.

    Direccion puede consultar todas y filtrar por fecha, profesor o estado. Un
    profesor normal solo ve las suyas.

    Query params opcionales:
      ?fecha=2026-04-23
      ?profesor_id=5   (solo Equipo Directivo)
      ?justificada=true|false
    """
    if request.user.is_equipo_directivo:
        qs = Ausencia.objects.select_related(
            'horario_entry__profesor'
        ).order_by('-fecha', 'horario_entry__hora')

        if profesor_id := request.query_params.get('profesor_id'):
            qs = qs.filter(horario_entry__profesor_id=profesor_id)
        if fecha := request.query_params.get('fecha'):
            qs = qs.filter(fecha=fecha)
        if justificada := request.query_params.get('justificada'):
            qs = qs.filter(justificada=justificada.lower() == 'true')
    else:
        if not hasattr(request.user, 'profesor'):
            return Response([])
        qs = Ausencia.objects.filter(
            horario_entry__profesor=request.user.profesor
        ).order_by('-fecha', 'horario_entry__hora')

    return Response(AusenciaSerializer(qs, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_ausencia(request):
    """
    Registra una ausencia en los tramos elegidos.

    Reglas:
    - El profesorado solo puede crear ausencias propias.
    - Direccion puede indicar profesor_id.
    - Si el profesor no tiene clase en ese tramo, se ignora porque no hay nada
      que cubrir.
    """
    serializer = CreateAusenciaSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    fecha = serializer.validated_data['fecha']
    horas = serializer.validated_data['horas']
    descripcion = serializer.validated_data.get('descripcion', '')

    # Direccion puede registrar ausencias de otros; el profesorado queda limitado a si mismo.
    if request.user.is_equipo_directivo and serializer.validated_data.get('profesor_id'):
        try:
            profesor = Profesor.objects.get(pk=serializer.validated_data['profesor_id'])
        except Profesor.DoesNotExist:
            return Response({'error': 'Profesor no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        if not hasattr(request.user, 'profesor'):
            return Response(
                {'error': 'Tu usuario no tiene un profesor vinculado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profesor = request.user.profesor

    dia = _get_dia_semana(fecha)
    if dia is None:
        return Response(
            {'error': 'La fecha indicada es fin de semana.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    creadas = []
    ignoradas = []
    ya_existentes = []

    for hora in horas:
        entries = HorarioEntry.objects.filter(
            profesor=profesor, dia=dia, hora=hora
        ).order_by('curso', 'aula', 'asignatura')

        if not entries.exists():
            ignoradas.append(hora)
            continue

        for entry in entries:
            ausencia, created = Ausencia.objects.get_or_create(
                fecha=fecha,
                horario_entry=entry,
                defaults={'descripcion': descripcion},
            )
            if created:
                creadas.append(AusenciaSerializer(ausencia).data)
            else:
                ya_existentes.append(AusenciaSerializer(ausencia).data)

    return Response(
        {
            'creadas': creadas,
            'ignoradas': ignoradas,
            'ya_existentes': ya_existentes,
            'mensaje': f'{len(creadas)} ausencia(s) registrada(s).',
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_ausencia(request, ausencia_id):
    """
    Elimina una ausencia.

    Un profesor puede borrar las suyas mientras sigan pendientes. Direccion puede
    corregir cualquier registro.
    """
    try:
        ausencia = Ausencia.objects.select_related(
            'horario_entry__profesor'
        ).get(pk=ausencia_id)
    except Ausencia.DoesNotExist:
        return Response({'error': 'Ausencia no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    if not request.user.is_equipo_directivo:
        if not hasattr(request.user, 'profesor') or ausencia.profesor != request.user.profesor:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if ausencia.justificada:
            return Response(
                {'error': 'No puedes eliminar una ausencia ya justificada.'},
                status=status.HTTP_403_FORBIDDEN,
            )

    ausencia.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH'])
@permission_classes([IsEquipoDireccion])
def justificar_ausencia(request, ausencia_id):
    """
    Cambia el estado justificada/no justificada.

    Lo dejamos solo para direccion porque afecta al parte oficial.
    """
    try:
        ausencia = Ausencia.objects.get(pk=ausencia_id)
    except Ausencia.DoesNotExist:
        return Response({'error': 'Ausencia no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = JustificarAusenciaSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    ausencia.justificada = serializer.validated_data['justificada']
    ausencia.save()

    return Response(AusenciaSerializer(ausencia).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ausencias_por_fecha(request, fecha):
    """
    Consulta auxiliar por fecha, pensada sobre todo para los partes PDF.
    """
    qs = Ausencia.objects.filter(fecha=fecha).select_related(
        'horario_entry__profesor'
    ).order_by('horario_entry__hora', 'horario_entry__profesor__nombre')

    return Response(AusenciaSerializer(qs, many=True).data)
