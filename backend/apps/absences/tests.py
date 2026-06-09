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
            'tareas': 'Leer el texto y completar las actividades 1 y 2.',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ausencia.objects.count(), 2)
        self.assertEqual(len(response.data['creadas']), 2)
        self.assertEqual(response.data['ignoradas'], [])
        self.assertEqual(
            response.data['creadas'][0]['tareas'],
            'Leer el texto y completar las actividades 1 y 2.',
        )

    def test_panel_diario_marca_guardias_de_profesores_ausentes(self):
        direccion = User.objects.create_user(
            email='direccion@iespoligonosur.org',
            password='Temporal123',
            role=User.EQUIPO_DIRECTIVO,
        )
        user = User.objects.create_user(
            email='fernando.duran@iespoligonosur.org',
            password='Temporal123',
            role=User.PROFESORADO,
        )
        profesor = Profesor.objects.create(nombre='Duran Correa, Fernando', user=user)

        HorarioEntry.objects.create(
            asignatura='Guardia',
            curso='GUARDIA A',
            aula='',
            profesor=profesor,
            dia='L',
            hora=2,
        )
        clase = HorarioEntry.objects.create(
            asignatura='Lengua',
            curso='1 ESO A',
            aula='101',
            profesor=profesor,
            dia='L',
            hora=2,
        )
        Ausencia.objects.create(
            fecha=datetime.date(2026, 5, 4),
            horario_entry=clase,
            descripcion='Asunto personal',
        )

        self.client.force_authenticate(user=direccion)
        response = self.client.get('/api/absences/panel/', {'fecha': '2026-05-04'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['resumen']['total_ausencias'], 1)
        self.assertEqual(response.data['resumen']['guardias_ausentes'], 1)
        self.assertEqual(response.data['guardias'][0]['modulo'], 'A')
        self.assertTrue(response.data['guardias'][0]['ausente'])

    def test_panel_diario_asigna_guardia_biblioteca_al_modulo_a(self):
        direccion = User.objects.create_user(
            email='direccion@iespoligonosur.org',
            password='Temporal123',
            role=User.EQUIPO_DIRECTIVO,
        )
        profesor = Profesor.objects.create(nombre='Paz Molina, Maria')

        HorarioEntry.objects.create(
            asignatura='Guardia',
            curso='GUARDIA BIBLIOTECA',
            aula='',
            profesor=profesor,
            dia='L',
            hora=5,
        )

        self.client.force_authenticate(user=direccion)
        response = self.client.get('/api/absences/panel/', {'fecha': '2026-05-04'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['guardias'][0]['modulo'], 'A')
