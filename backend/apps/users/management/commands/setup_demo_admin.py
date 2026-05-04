from django.core.management.base import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    help = 'Crea o actualiza un usuario administrador de prueba para la demo local.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            default='admin@iespoligonosur.org',
            help='Email del usuario demo.',
        )
        parser.add_argument(
            '--password',
            default='admin1234',
            help='Contraseña temporal del usuario demo.',
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'role': User.EQUIPO_DIRECTIVO,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'must_change_password': False,
            },
        )

        user.role = User.EQUIPO_DIRECTIVO
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.must_change_password = False
        user.set_password(password)
        user.save()

        accion = 'creado' if created else 'actualizado'
        self.stdout.write(self.style.SUCCESS(f'Usuario demo {accion}: {email}'))
