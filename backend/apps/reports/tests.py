import datetime
import shutil
import tempfile

from django.core import mail
from django.core.files.base import ContentFile
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.reports.models import ParteAusencias
from apps.reports.pdf_generator import _asignar_modulo_guardia
from apps.reports.services import generar_partes_del_dia
from apps.schedules.models import HorarioEntry
from apps.users.models import Profesor, User


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
        otro_directivo = User.objects.create_user(
            email='jefatura@iespoligonosur.org',
            password='Temporal123',
            role=User.EQUIPO_DIRECTIVO,
        )
        User.objects.create_user(
            email='profesor@iespoligonosur.org',
            password='Temporal123',
            role=User.PROFESORADO,
        )
        parte = ParteAusencias.objects.create(
            fecha=datetime.date(2026, 5, 4),
            tipo=ParteAusencias.GENERAL,
        )
        parte.pdf_file.save('parte_test.pdf', ContentFile(b'%PDF-1.4\n'), save=True)

        self.client.force_authenticate(user=user)
        response = self.client.post(f'/api/reports/{parte.id}/enviar/', {}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertCountEqual(mail.outbox[0].to, [user.email, otro_directivo.email])
        self.assertEqual(len(mail.outbox[0].attachments), 1)

    def test_generacion_diaria_crea_parte_comun(self):
        partes = generar_partes_del_dia(datetime.date(2026, 5, 4))

        self.assertEqual(len(partes), 1)
        self.assertEqual(partes[0].tipo, ParteAusencias.GENERAL)
        self.assertTrue(partes[0].pdf_file.name.endswith('ies_completo.pdf'))


class ParteModuloTests(APITestCase):
    def test_guardia_biblioteca_se_considera_modulo_a(self):
        guardia = HorarioEntry(
            asignatura='Guardia',
            curso='GUARDIA BIBLIOTECA',
            aula='',
            profesor=Profesor(nombre='Paz Molina, Maria'),
            dia='L',
            hora=5,
        )

        self.assertEqual(_asignar_modulo_guardia(guardia), 'A')
