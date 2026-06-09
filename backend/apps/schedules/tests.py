from django.test import TestCase
from rest_framework.test import APITestCase

from apps.schedules.models import HorarioEntry
from apps.schedules.services import importar_horario, importar_horario_desde_bytes
from apps.users.models import Profesor, User


class HorarioImportTests(TestCase):
    def test_importa_mismo_profesor_misma_hora_para_varios_grupos(self):
        contenido = "\n".join([
            "Francés opt.2º eso\t2º A ESO\t200\tRodríguez Pueyo, Lucía\tL\t2",
            "Francés opt.2º eso\t2º B ESO\t200\tRodríguez Pueyo, Lucía\tL\t2",
            "Francés opt.2º eso\t2º C ESO\t200\tRodríguez Pueyo, Lucía\tL\t2",
            "Francés opt.2º eso\t2º D ESO\t200\tRodríguez Pueyo, Lucía\tL\t2",
        ])

        stats = importar_horario(contenido)

        self.assertEqual(stats['filas_importadas'], 4)
        self.assertEqual(stats['filas_duplicadas'], 0)
        self.assertEqual(HorarioEntry.objects.count(), 4)
        self.assertEqual(Profesor.objects.count(), 1)

    def test_omite_solo_duplicados_exactos(self):
        fila = "Música\t1º A ESO\t111\tGonzález Macías, Rocío de la Salud\tL\t1"
        stats = importar_horario(f"{fila}\n{fila}")

        self.assertEqual(stats['filas_importadas'], 1)
        self.assertEqual(stats['filas_duplicadas'], 1)
        self.assertEqual(HorarioEntry.objects.count(), 1)

    def test_importa_fichero_cp1252(self):
        contenido = "Música\t1º A ESO\t111\tGonzález Macías, Rocío de la Salud\tL\t1"
        stats = importar_horario_desde_bytes(contenido.encode('cp1252'))

        self.assertEqual(stats['filas_importadas'], 1)
        self.assertEqual(HorarioEntry.objects.first().profesor.nombre, "González Macías, Rocío de la Salud")


class HorarioListApiTests(APITestCase):
    def test_filtra_por_asignatura(self):
        user = User.objects.create_user(
            email='direccion@iespoligonosur.org',
            password='Temporal123',
            role=User.EQUIPO_DIRECTIVO,
        )
        profesor = Profesor.objects.create(nombre='Martinez Lopez, Ana')
        HorarioEntry.objects.create(
            asignatura='Lengua Castellana',
            curso='1 ESO A',
            aula='101',
            profesor=profesor,
            dia='L',
            hora=1,
        )
        HorarioEntry.objects.create(
            asignatura='Matematicas',
            curso='1 ESO A',
            aula='102',
            profesor=profesor,
            dia='L',
            hora=2,
        )

        self.client.force_authenticate(user=user)
        response = self.client.get('/api/schedules/', {'asignatura': 'lengua'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['asignatura'], 'Lengua Castellana')
