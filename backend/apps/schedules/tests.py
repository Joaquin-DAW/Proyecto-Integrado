from django.test import TestCase

from apps.schedules.models import HorarioEntry
from apps.schedules.services import importar_horario, importar_horario_desde_bytes
from apps.users.models import Profesor


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
