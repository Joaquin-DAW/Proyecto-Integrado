from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, Profesor


class UserSerializer(serializers.ModelSerializer):
    """Datos de usuario que se pueden mandar al frontend sin exponer contraseña."""

    class Meta:
        model = User
        fields = ('id', 'email', 'role', 'must_change_password', 'is_active')
        read_only_fields = ('id', 'must_change_password')


class ProfesorSerializer(serializers.ModelSerializer):
    """Profesor con su cuenta enlazada cuando ya existe."""

    user = UserSerializer(read_only=True)
    email_institucional = serializers.SerializerMethodField()

    class Meta:
        model = Profesor
        fields = ('id', 'nombre', 'user', 'email_institucional')

    def get_email_institucional(self, obj):
        return Profesor.generar_email(obj.nombre)


class ProfesorListSerializer(serializers.ModelSerializer):
    """Version ligera para tablas y buscadores."""

    tiene_cuenta = serializers.BooleanField(source='user', read_only=True)
    email_institucional = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profesor
        fields = ('id', 'nombre', 'tiene_cuenta', 'email_institucional', 'user')

    def get_email_institucional(self, obj):
        return Profesor.generar_email(obj.nombre)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # En la tabla interesa un si/no, no el objeto User completo.
        data['tiene_cuenta'] = instance.user is not None
        return data


class CreateUserForProfesorSerializer(serializers.Serializer):
    """
    Datos necesarios para crear la cuenta de un profesor que ya esta importado.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default=User.PROFESORADO)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese email.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Cambio de contraseña, tanto en primer acceso como mas adelante."""

    password_actual = serializers.CharField(write_only=True)
    nueva_password = serializers.CharField(write_only=True)

    def validate_nueva_password(self, value):
        validate_password(value)
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Formulario minimo para pedir un enlace de recuperacion."""

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Datos que llegan desde el enlace de recuperacion."""

    uid = serializers.CharField()
    token = serializers.CharField()
    nueva_password = serializers.CharField(write_only=True)

    def validate_nueva_password(self, value):
        validate_password(value)
        return value


class UpdateUserSerializer(serializers.ModelSerializer):
    """Campos editables de una cuenta desde direccion."""

    class Meta:
        model = User
        fields = ('email', 'role', 'is_active')

    def validate_email(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Ese email ya está en uso.")
        return value
