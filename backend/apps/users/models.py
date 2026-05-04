"""
Modelos relacionados con las cuentas y el profesorado.

Aqui hay dos conceptos separados a proposito:
- User es la cuenta que inicia sesion en Horarium.
- Profesor es la persona que aparece en el fichero de horarios.

No todos los profesores tienen por que tener usuario desde el primer momento.
Primero se importa el horario del centro y mas adelante direccion decide a quien
le crea una cuenta de acceso.
"""
import unicodedata
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Manager propio para iniciar sesion con email, no con username.

class UserManager(BaseUserManager):
    """Pequeña adaptación del manager de Django para trabajar solo con email."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', User.EQUIPO_DIRECTIVO)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# Cuenta de acceso a la aplicacion.

class User(AbstractBaseUser, PermissionsMixin):
    """
    Usuario que puede entrar en Horarium.

    must_change_password se deja a True cuando se crea una cuenta desde direccion,
    asi el profesor cambia la contraseña temporal en su primer acceso.
    """

    PROFESORADO = 'PROFESORADO'
    EQUIPO_DIRECTIVO = 'EQUIPO_DIRECTIVO'

    ROLE_CHOICES = [
        (PROFESORADO, 'Profesorado'),
        (EQUIPO_DIRECTIVO, 'Equipo Directivo'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=PROFESORADO)
    must_change_password = models.BooleanField(default=True)

    # Django admin necesita estos campos aunque el login real vaya por email.
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []   # Con email y password basta para crear un usuario.

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.email

    @property
    def is_equipo_directivo(self):
        return self.role == self.EQUIPO_DIRECTIVO

    @property
    def is_profesorado(self):
        return self.role == self.PROFESORADO


# Profesor importado desde el horario del centro.

class Profesor(models.Model):
    """
    Se guarda el nombre tal cual viene en Datos_horarios.txt, normalmente con el
    formato "Apellidos, Nombre". La cuenta de usuario es opcional y se enlaza
    cuando el profesor necesita entrar a la plataforma.
    """

    nombre = models.CharField(max_length=200, unique=True)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profesor',
    )

    class Meta:
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @staticmethod
    def generar_email(nombre_raw: str) -> str:
        """
        Propone el correo institucional a partir del nombre del fichero.

        Regla usada en el proyecto:
        primer_nombre.primer_apellido@iespoligonosur.org

        Ejemplo: "Durán Correa, Fernando" pasa a fernando.duran@iespoligonosur.org.
        Se eliminan acentos para evitar correos raros o incompatibles.
        """
        DOMINIO = '@iespoligonosur.org'

        partes = nombre_raw.split(',', 1)
        apellidos_part = partes[0].strip()
        nombre_part = partes[1].strip() if len(partes) > 1 else ''

        primer_apellido = apellidos_part.split()[0] if apellidos_part else 'apellido'
        primer_nombre = nombre_part.split()[0] if nombre_part else 'nombre'

        def strip_accents(s: str) -> str:
            return ''.join(
                c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn'
            )

        email_local = f"{strip_accents(primer_nombre)}.{strip_accents(primer_apellido)}".lower()
        return f"{email_local}{DOMINIO}"
