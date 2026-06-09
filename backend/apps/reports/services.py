"""
Funciones para crear partes y dejarlos guardados.

Las usa tanto la API como Celery. Asi se evita que el parte manual y el parte
automatico terminen haciendo cosas distintas con el tiempo.
"""
import datetime

from django.core.files.base import ContentFile
from django.core.mail import EmailMessage

from apps.users.models import User
from .models import ParteAusencias
from .pdf_generator import generar_pdf


TIPOS_PARTE = (
    ParteAusencias.GENERAL,
    ParteAusencias.MODULO_A,
    ParteAusencias.MODULO_B,
)


def generar_y_guardar_parte(fecha: datetime.date, tipo: str) -> ParteAusencias:
    """
    Genera el PDF y lo guarda en el registro correspondiente.

    Si el parte ya existia, se reemplaza el archivo. Esto viene bien cuando se
    anade una ausencia tarde y hay que regenerar el documento.
    """
    if tipo not in TIPOS_PARTE:
        raise ValueError(f"Tipo de parte invalido: {tipo!r}. Usa 'G', 'A' o 'B'.")

    pdf_bytes = generar_pdf(fecha, tipo)

    sufijo = 'ies_completo' if tipo == ParteAusencias.GENERAL else f"modulo_{tipo}"
    nombre_fichero = f"parte_{fecha.isoformat()}_{sufijo}.pdf"

    parte, _ = ParteAusencias.objects.get_or_create(fecha=fecha, tipo=tipo)
    parte.pdf_file.save(nombre_fichero, ContentFile(pdf_bytes), save=True)

    return parte


def generar_partes_del_dia(fecha: datetime.date = None) -> list:
    """
    Genera el parte comun del IES para una fecha. Si no se pasa fecha, usa hoy.

    Los partes A/B siguen existiendo para uso manual, pero el flujo diario se
    centra en el documento comun que pidio el centro.
    """
    if fecha is None:
        fecha = datetime.date.today()

    return [
        generar_y_guardar_parte(fecha, ParteAusencias.GENERAL),
    ]


def emails_equipo_directivo() -> list:
    """Correos activos que deben recibir los partes oficiales."""
    return list(
        User.objects.filter(
            role=User.EQUIPO_DIRECTIVO,
            is_active=True,
        )
        .exclude(email='')
        .values_list('email', flat=True)
    )


def enviar_parte_a_equipo_directivo(parte: ParteAusencias) -> int:
    """
    Envia un parte a todas las cuentas activas de equipo directivo.

    Devuelve el numero de destinatarios para poder mostrarlo en la API o en la
    salida de la tarea programada.
    """
    if not parte.pdf_file:
        raise ValueError('Este parte aun no tiene PDF generado.')

    destinatarios = emails_equipo_directivo()
    if not destinatarios:
        return 0

    etiqueta = parte.get_tipo_display()
    fecha_legible = parte.fecha.strftime('%d/%m/%Y')
    email = EmailMessage(
        subject=f'Parte de ausencias {fecha_legible} - {etiqueta}',
        body=(
            f'Adjuntamos el parte de ausencias del {fecha_legible} '
            f'correspondiente a {etiqueta}.'
        ),
        to=destinatarios,
    )
    email.attach_file(parte.pdf_file.path)
    email.send(fail_silently=False)

    return len(destinatarios)
