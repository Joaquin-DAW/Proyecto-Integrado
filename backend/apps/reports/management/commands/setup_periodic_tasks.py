"""
Comando para dejar creada la tarea periodica de los partes.

django-celery-beat guarda la programacion en PostgreSQL. Por eso se registra con
un comando de management y no solo en settings.py: asi queda estable aunque se
reinicien los contenedores.
"""
from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):
    help = 'Registra la tarea periódica de generación de partes de ausencias.'

    def handle(self, *args, **options):
        # 08:00 de lunes a viernes, con la zona horaria del centro.
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='8',
            day_of_week='1-5',      # lunes (1) a viernes (5)
            day_of_month='*',
            month_of_year='*',
            timezone='Europe/Madrid',
        )

        tarea, creada = PeriodicTask.objects.get_or_create(
            name='Generar partes de ausencias diarios',
            defaults={
                'task': 'reports.generar_partes_diarios',
                'crontab': schedule,
                'enabled': True,
            },
        )

        if not creada:
            # Si el comando se ejecuta otra vez, se corrige la tarea existente.
            tarea.crontab = schedule
            tarea.enabled = True
            tarea.save()
            self.stdout.write(self.style.WARNING('Tarea ya existía — actualizada.'))
        else:
            self.stdout.write(self.style.SUCCESS('Tarea periódica registrada correctamente.'))

        self.stdout.write(f'  Nombre: {tarea.name}')
        self.stdout.write(f'  Crontab: {schedule}')
