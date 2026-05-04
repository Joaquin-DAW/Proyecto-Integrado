"""
Arranque de Celery para Horarium.

Se usa para generar tareas fuera de la peticion HTTP y para lanzar el parte de
ausencias cada mañana con Celery Beat.
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarium.settings.development')

app = Celery('horarium')

# Carga las variables CELERY_* definidas en settings.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Busca tasks.py en las apps instaladas, por ejemplo apps.reports.tasks.
app.autodiscover_tasks()
