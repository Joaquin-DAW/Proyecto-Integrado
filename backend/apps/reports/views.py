import datetime
from django.core.mail import EmailMessage
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers

from apps.users.permissions import IsEquipoDireccion
from .models import ParteAusencias
from .services import generar_y_guardar_parte


class ParteSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = ParteAusencias
        fields = ('id', 'fecha', 'tipo', 'tipo_display', 'generado_en', 'pdf_url')

    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.pdf_file.url) if request else obj.pdf_file.url
        return None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_partes(request):
    """
    Lista los partes generados, con filtros simples para buscar por dia o modulo:
      ?fecha=2026-04-23
      ?tipo=A|B
    """
    qs = ParteAusencias.objects.order_by('-fecha', 'tipo')

    if fecha := request.query_params.get('fecha'):
        qs = qs.filter(fecha=fecha)
    if tipo := request.query_params.get('tipo'):
        qs = qs.filter(tipo=tipo.upper())

    return Response(ParteSerializer(qs, many=True, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([IsEquipoDireccion])
def generar_parte(request):
    """
    Genera un parte bajo demanda para una fecha y modulo.

    Si ya habia uno igual, se pisa el PDF anterior con la version nueva.

    Body:
      { "fecha": "2026-04-23", "tipo": "A" }
    """
    fecha_str = request.data.get('fecha')
    tipo = request.data.get('tipo', '').upper()

    if not fecha_str:
        return Response({'error': 'El campo fecha es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
    if tipo not in ('A', 'B'):
        return Response({'error': "El campo tipo debe ser 'A' o 'B'."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        fecha = datetime.date.fromisoformat(fecha_str)
    except ValueError:
        return Response({'error': 'Formato de fecha inválido. Usa YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        parte = generar_y_guardar_parte(fecha, tipo)
    except Exception as exc:
        return Response({'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(
        ParteSerializer(parte, context={'request': request}).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def descargar_parte(request, parte_id):
    """
    Devuelve el PDF guardado para descargarlo desde el navegador.
    """
    try:
        parte = ParteAusencias.objects.get(pk=parte_id)
    except ParteAusencias.DoesNotExist:
        return Response({'error': 'Parte no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if not parte.pdf_file:
        return Response({'error': 'Este parte aún no tiene PDF generado.'}, status=status.HTTP_404_NOT_FOUND)

    return FileResponse(
        parte.pdf_file.open('rb'),
        as_attachment=True,
        filename=f"parte_{parte.fecha}_{parte.tipo}.pdf",
        content_type='application/pdf',
    )


@api_view(['POST'])
@permission_classes([IsEquipoDireccion])
def enviar_parte_email(request, parte_id):
    """
    Envia el PDF al correo del usuario de direccion que esta autenticado.
    """
    try:
        parte = ParteAusencias.objects.get(pk=parte_id)
    except ParteAusencias.DoesNotExist:
        return Response({'error': 'Parte no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if not parte.pdf_file:
        return Response({'error': 'Este parte aun no tiene PDF generado.'}, status=status.HTTP_404_NOT_FOUND)

    email = EmailMessage(
        subject=f'Parte de ausencias {parte.fecha} - Modulo {parte.tipo}',
        body=(
            f'Adjuntamos el parte de ausencias del {parte.fecha} '
            f'correspondiente al Modulo {parte.tipo}.'
        ),
        to=[request.user.email],
    )
    email.attach_file(parte.pdf_file.path)
    email.send(fail_silently=False)

    return Response({'mensaje': f'Parte enviado a {request.user.email}.'})
