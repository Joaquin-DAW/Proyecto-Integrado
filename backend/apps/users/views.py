from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User, Profesor
from .permissions import IsEquipoDireccion
from .serializers import (
    ProfesorSerializer,
    ProfesorListSerializer,
    CreateUserForProfesorSerializer,
    ChangePasswordSerializer,
    UpdateUserSerializer,
    UserSerializer,
)


# Consultas sobre profesores importados del horario.

class ProfesorListView(generics.ListAPIView):
    """
    Lista todo el profesorado del centro.

    Direccion lo usa para crear cuentas y el profesorado para localizar a otros
    compañeros dentro del horario.
    """
    queryset = Profesor.objects.select_related('user').order_by('nombre')
    serializer_class = ProfesorListSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['nombre']
    pagination_class = None


class ProfesorDetailView(generics.RetrieveAPIView):
    """
    Detalle de un profesor, incluida su cuenta si ya la tiene vinculada.
    """
    queryset = Profesor.objects.select_related('user')
    serializer_class = ProfesorSerializer
    permission_classes = [IsAuthenticated]


# Alta y mantenimiento de cuentas. Solo lo usa direccion.

@api_view(['POST'])
@permission_classes([IsEquipoDireccion])
def crear_cuenta_profesor(request, profesor_id):
    """
    Crea una cuenta para un profesor que ya esta en el horario.

    El email se calcula con la regla del centro y la contraseña temporal solo se
    muestra una vez en el frontend.
    """
    import secrets, string

    try:
        profesor = Profesor.objects.get(pk=profesor_id)
    except Profesor.DoesNotExist:
        return Response({'error': 'Profesor no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if profesor.user is not None:
        return Response(
            {'error': 'Este profesor ya tiene una cuenta de acceso.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = Profesor.generar_email(profesor.nombre)

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': f'Ya existe un usuario con el email {email}.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    alphabet = string.ascii_letters + string.digits
    password_temporal = ''.join(secrets.choice(alphabet) for _ in range(12))

    user = User.objects.create_user(
        email=email,
        password=password_temporal,
        role=User.PROFESORADO,
        must_change_password=True,
    )
    profesor.user = user
    profesor.save()

    return Response(
        {
            'usuario': UserSerializer(user).data,
            'password_temporal': password_temporal,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsEquipoDireccion])
def actualizar_usuario(request, user_id):
    """
    Permite corregir email, rol o estado activo de una cuenta.
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateUserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(UserSerializer(user).data)


@api_view(['DELETE'])
@permission_classes([IsEquipoDireccion])
def eliminar_usuario(request, user_id):
    """
    Borra la cuenta de acceso, pero no elimina al profesor del horario.
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if user == request.user:
        return Response(
            {'error': 'No puedes eliminar tu propia cuenta.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# Endpoints del usuario que esta autenticado.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mi_perfil(request):
    """
    Devuelve la cuenta actual y, si procede, el profesor asociado.
    """
    data = UserSerializer(request.user).data
    if hasattr(request.user, 'profesor'):
        data['profesor'] = ProfesorSerializer(request.user.profesor).data
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cambiar_password(request):
    """
    Cambia la contraseña propia.

    Cuando el cambio sale bien se quita must_change_password para dejar entrar a
    las pantallas normales.
    """
    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if not request.user.check_password(serializer.validated_data['password_actual']):
        return Response(
            {'error': 'La contraseña actual no es correcta.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    request.user.set_password(serializer.validated_data['nueva_password'])
    request.user.must_change_password = False
    request.user.save()

    return Response({'mensaje': 'Contraseña actualizada correctamente.'})
