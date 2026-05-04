"""
Funciones para crear partes y dejarlos guardados.

Las usa tanto la API como Celery. Asi se evita que el parte manual y el parte
automatico terminen haciendo cosas distintas con el tiempo.
"""
import datetime
from django.core.files.base import ContentFile

from .models import ParteAusencias
from .pdf_generator import generar_pdf


def generar_y_guardar_parte(fecha: datetime.date, tipo: str) -> ParteAusencias:
    """
    Genera el PDF y lo guarda en el registro correspondiente.

    Si el parte ya existia, se reemplaza el archivo. Esto viene bien cuando se
    añade una ausencia tarde y hay que regenerar el documento.
    """
    if tipo not in (ParteAusencias.MODULO_A, ParteAusencias.MODULO_B):
        raise ValueError(f"Tipo de módulo inválido: {tipo!r}. Usa 'A' o 'B'.")

    pdf_bytes = generar_pdf(fecha, tipo)

    nombre_fichero = f"parte_{fecha.isoformat()}_modulo_{tipo}.pdf"

    parte, _ = ParteAusencias.objects.get_or_create(fecha=fecha, tipo=tipo)
    parte.pdf_file.save(nombre_fichero, ContentFile(pdf_bytes), save=True)

    return parte


def generar_partes_del_dia(fecha: datetime.date = None) -> list:
    """
    Genera los dos modulos para una fecha. Si no se pasa fecha, usa hoy.
    """
    if fecha is None:
        fecha = datetime.date.today()

    return [
        generar_y_guardar_parte(fecha, ParteAusencias.MODULO_A),
        generar_y_guardar_parte(fecha, ParteAusencias.MODULO_B),
    ]
