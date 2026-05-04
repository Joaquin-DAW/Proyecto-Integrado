# Ajuste manual: permite clases compartidas y bloquea solo duplicados exactos.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0002_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='horarioentry',
            unique_together={('profesor', 'dia', 'hora', 'asignatura', 'curso', 'aula')},
        ),
    ]
