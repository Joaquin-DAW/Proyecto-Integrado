"""
Tareas de Celery relacionadas con los partes.

Celery Beat llama a generar_partes_diarios cada mañana lectiva. La programacion
queda guardada en la base de datos con django-celery-beat, asi tambien se puede
revisar desde el admin de Django.
"""
import datetime
from celery import shared_task


@shared_task(name='reports.generar_partes_diarios')
def generar_partes_diarios():
    """
    Genera los partes A y B para el dia actual.

    El import queda dentro de la funcion para que Celery arranque sin pelearse
    con las importaciones de Django.
    """
    from .services import generar_partes_del_dia

    hoy = datetime.date.today()

    # Los sabados y domingos no hay parte que generar.
    if hoy.weekday() > 4:
        return f'Fin de semana ({hoy}) — tarea omitida.'

    partes = generar_partes_del_dia(hoy)
    return f'Partes generados para {hoy}: {[str(p) for p in partes]}'
