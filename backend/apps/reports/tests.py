import datetime
import shutil
import tempfile

from django.core import mail
from django.core.files.base import ContentFile
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.reports.models import ParteAusencias
from apps.users.models import User


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ParteEmailTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls._media_root = tempfile.mkdtemp()
        cls._override = override_settings(MEDIA_ROOT=cls._media_root)
        cls._override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._override.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)

    def test_equipo_directivo_puede_enviar_parte_por_email(self):
        user = User.objects.create_user(
            email='direccion@iespoligonosur.org',
            password='Temporal123',
            role=User.EQUIPO_DIRECTIVO,
        )
        parte = ParteAusencias.objects.create(
            fecha=datetime.date(2026, 5, 4),
            tipo=ParteAusencias.MODULO_A,
        )
        parte.pdf_file.save('parte_test.pdf', ContentFile(b'%PDF-1.4\n'), save=True)

        self.client.force_authenticate(user=user)
        response = self.client.post(f'/api/reports/{parte.id}/enviar/', {}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [user.email])
        self.assertEqual(len(mail.outbox[0].attachments), 1)
