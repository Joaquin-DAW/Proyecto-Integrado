import datetime

from rest_framework.test import APITestCase

from apps.absences.models import Ausencia
from apps.schedules.models import HorarioEntry
from apps.users.models import Profesor, User


class AusenciaCreationTests(APITestCase):
    def test_crea_ausencia_para_todas_las_entradas_del_mismo_tramo(self):
        user = User.objects.create_user(
            email='lucia.rodriguez@iespoligonosur.org',
            password='Temporal123',
            role=User.PROFESORADO,
        )
        profesor = Profesor.objects.create(nombre='Rodríguez Pueyo, Lucía', user=user)

        HorarioEntry.objects.create(
            asignatura='Francés opt.2º eso',
            curso='2º A ESO',
            aula='200',
            profesor=profesor,
            dia='L',
            hora=2,
        )
        HorarioEntry.objects.create(
            asignatura='Francés opt.2º eso',
            curso='2º B ESO',
            aula='200',
            profesor=profesor,
            dia='L',
            hora=2,
        )

        self.client.force_authenticate(user=user)
        response = self.client.post('/api/absences/crear/', {
            'fecha': datetime.date(2026, 5, 4).isoformat(),
            'horas': [2],
            'descripcion': 'Cita medica',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ausencia.objects.count(), 2)
        self.assertEqual(len(response.data['creadas']), 2)
        self.assertEqual(response.data['ignoradas'], [])
