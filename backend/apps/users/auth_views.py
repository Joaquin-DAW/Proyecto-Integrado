"""
Login y recuperacion de contraseña.

No se usa directamente TokenObtainPairView porque el frontend necesita recibir
tambien el rol y must_change_password nada mas iniciar sesion.
"""
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserSerializer,
)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class LoginView(APIView):
    """
    Devuelve tokens JWT y los datos basicos del usuario.

    Response:
    {
        "access": "...",
        "refresh": "...",
        "usuario": { "id", "email", "role", "must_change_password" }
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Credenciales incorrectas.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return Response(
                {'error': 'Credenciales incorrectas.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {'error': 'Esta cuenta está desactivada.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'usuario': UserSerializer(user).data,
        })


class PasswordResetRequestView(APIView):
    """
    Envia un enlace de recuperacion si el email pertenece a una cuenta activa.

    La respuesta es generica a proposito para no confirmar si un correo existe.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email, is_active=True).first()

        if user:
            token = PasswordResetTokenGenerator().make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            frontend_url = settings.FRONTEND_URL.rstrip('/')
            reset_url = f'{frontend_url}/reset-password?uid={uid}&token={token}'

            send_mail(
                subject='Recuperacion de contraseña - Horarium',
                message=(
                    'Has solicitado recuperar tu contraseña en Horarium.\n\n'
                    f'Abre este enlace para crear una nueva contraseña:\n{reset_url}\n\n'
                    'Si no has solicitado este cambio, puedes ignorar este mensaje.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        return Response({
            'mensaje': 'Si existe una cuenta con ese email, recibiras un enlace de recuperacion.'
        })


class PasswordResetConfirmView(APIView):
    """
    Cambia la contraseña usando el uid y token del enlace enviado por email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = urlsafe_base64_decode(serializer.validated_data['uid']).decode()
            user = User.objects.get(pk=user_id, is_active=True)
        except (TypeError, ValueError, OverflowError, UnicodeDecodeError, User.DoesNotExist):
            return Response({'error': 'Enlace de recuperacion invalido.'}, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['token']
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'error': 'Enlace de recuperacion caducado o invalido.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['nueva_password'])
        user.must_change_password = False
        user.save()

        return Response({'mensaje': 'Contraseña actualizada correctamente.'})
