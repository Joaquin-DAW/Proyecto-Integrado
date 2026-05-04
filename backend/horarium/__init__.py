# Importa Celery al arrancar Django para que las tareas queden disponibles.
from .celery import app as celery_app

__all__ = ('celery_app',)
