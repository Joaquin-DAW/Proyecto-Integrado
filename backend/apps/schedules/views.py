import base64
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsEquipoDireccion
from .models import HorarioEntry
from .serializers import HorarioEntrySerializer, HorarioImportSerializer
from .services import importar_horario_desde_bytes


class HorarioListView(generics.ListAPIView):
    """
    Devuelve entradas del horario del centro.

    Admite filtros por query params:
      ?profesor_id=5
      ?dia=L
      ?hora=3

    El profesorado puede ver el horario completo porque para las guardias y
    consultas internas hace falta saber quien esta en cada tramo.
    """
    serializer_class = HorarioEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = HorarioEntry.objects.select_related('profesor').order_by('dia', 'hora', 'profesor__nombre')

        p = self.request.query_params
        if p.get('profesor_id'):
            qs = qs.filter(profesor_id=p['profesor_id'])
        if p.get('profesor_nombre'):
            qs = qs.filter(profesor__nombre__icontains=p['profesor_nombre'])
        if p.get('dia'):
            qs = qs.filter(dia=p['dia'])
        if p.get('hora'):
            qs = qs.filter(hora=p['hora'])
        if p.get('grupo'):
            qs = qs.filter(curso__icontains=p['grupo'])
        if p.get('aula'):
            qs = qs.filter(aula__icontains=p['aula'])

        return qs


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mi_horario(request):
    """
    Horario del profesor autenticado.

    Si la cuenta no esta vinculada a un Profesor, se devuelve una lista vacia.
    """
    if not hasattr(request.user, 'profesor'):
        return Response([])

    entradas = (
        HorarioEntry.objects
        .filter(profesor=request.user.profesor)
        .order_by('dia', 'hora')
    )
    return Response(HorarioEntrySerializer(entradas, many=True).data)


@api_view(['POST'])
@permission_classes([IsEquipoDireccion])
def importar_horario(request):
    """
    Importa el fichero de horarios y reemplaza todo lo anterior.

    Solo direccion puede hacerlo porque cambia la base de horarios completa.

    Acepta:
      - multipart/form-data con campo 'fichero'
      - JSON con campo 'fichero_base64' (string base64)
    """
    serializer = HorarioImportSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if serializer.validated_data.get('fichero'):
        raw = serializer.validated_data['fichero'].read()
    else:
        try:
            raw = base64.b64decode(serializer.validated_data['fichero_base64'])
        except Exception:
            return Response(
                {'error': 'El campo fichero_base64 no es un base64 válido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    try:
        stats = importar_horario_desde_bytes(raw)
    except ValueError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(stats, status=status.HTTP_201_CREATED)
