"""
Importacion del fichero Datos_horarios.txt.

El archivo llega separado por tabuladores con seis columnas:
asignatura, curso, aula, profesor, dia y hora. Este modulo valida esas lineas,
crea los profesores que falten y reemplaza el horario completo por el nuevo.

Aqui no se crean cuentas de usuario. Un profesor puede existir en el horario sin
tener acceso a la web; eso se gestiona despues desde direccion.
"""
import unicodedata
from django.db import transaction

from apps.users.models import Profesor
from .models import HorarioEntry

SEPARADOR = '\t'

DIAS_VALIDOS = {'L', 'M', 'X', 'J', 'V'}


# Punto de entrada usado por la API cuando se sube el fichero.

def importar_horario_desde_bytes(raw: bytes) -> dict:
    """
    Intenta abrir el fichero con las codificaciones mas normales en Windows.
    En algunos equipos el txt llega como cp1252, por eso no se asume solo UTF-8.
    """
    for encoding in ('utf-8-sig', 'utf-8', 'latin-1', 'cp1252'):
        try:
            contenido = raw.decode(encoding)
            return importar_horario(contenido)
        except UnicodeDecodeError:
            continue
    raise ValueError("No se pudo decodificar el fichero. Usa UTF-8 o Latin-1.")


@transaction.atomic
def importar_horario(contenido: str) -> dict:
    """
    Parsea el texto del horario y lo guarda como reemplazo completo.

    Devuelve estadisticas para que el frontend pueda enseñar si hubo duplicados
    o lineas con error sin tener que volver a analizar el fichero.
    """
    lineas = [l for l in contenido.splitlines() if l.strip()]

    stats = {
        'total_lineas': len(lineas),
        'filas_importadas': 0,
        'filas_duplicadas': 0,
        'profesores_creados': 0,
        'filas_con_error': 0,
        'errores': [],
    }

    entradas = []
    entradas_vistas = set()
    profesores_cache = {}   # evita consultar la BD una y otra vez para el mismo nombre
    profesores_nuevos = 0

    for num_linea, linea in enumerate(lineas, start=1):
        try:
            entrada, profesor, es_nuevo = _parsear_linea(linea, profesores_cache)
            clave = (
                profesor.pk,
                entrada.dia,
                entrada.hora,
                entrada.asignatura,
                entrada.curso,
                entrada.aula,
            )
            if clave in entradas_vistas:
                stats['filas_duplicadas'] += 1
                continue
            entradas_vistas.add(clave)
            entradas.append(entrada)
            if es_nuevo:
                profesores_nuevos += 1
        except ValueError as exc:
            stats['filas_con_error'] += 1
            stats['errores'].append(f"Línea {num_linea}: {exc}")

    # Reemplazo completo: si la importacion falla, transaction.atomic revierte todo.
    HorarioEntry.objects.all().delete()
    HorarioEntry.objects.bulk_create(entradas)

    stats['filas_importadas'] = len(entradas)
    stats['profesores_creados'] = profesores_nuevos
    # Nombres antiguos que puede seguir esperando alguna pantalla del frontend.
    stats['importados'] = stats['filas_importadas']
    stats['profesores'] = stats['profesores_creados']

    return stats


# Funciones pequeñas del parser. Se dejan separadas para probarlas mejor.

def _parsear_linea(linea: str, cache: dict) -> tuple:
    """
    Convierte una linea del TXT en un HorarioEntry sin guardarlo todavia.

    Si algo no cuadra se lanza ValueError con un mensaje entendible para el
    resumen de importacion.
    """
    campos = linea.split(SEPARADOR)

    if len(campos) < 6:
        raise ValueError(
            f"Se esperaban 6 campos separados por tabulador, se encontraron {len(campos)}: {linea!r}"
        )

    asignatura = campos[0].strip()
    curso      = campos[1].strip()
    aula       = campos[2].strip()
    nombre_raw = campos[3].strip()
    dia        = campos[4].strip()
    hora_str   = campos[5].strip()

    if not asignatura:
        raise ValueError("El campo Asignatura está vacío")

    if not nombre_raw:
        raise ValueError("El campo Profesor está vacío")

    if dia not in DIAS_VALIDOS:
        raise ValueError(f"Día inválido: {dia!r}. Valores permitidos: L, M, X, J, V")

    try:
        hora = int(hora_str)
    except ValueError:
        raise ValueError(f"Hora inválida: {hora_str!r}. Debe ser un número entre 1 y 14")

    if not (1 <= hora <= 14):
        raise ValueError(f"Hora fuera de rango: {hora}. Debe estar entre 1 y 14")

    profesor, es_nuevo = _obtener_o_crear_profesor(nombre_raw, cache)

    entrada = HorarioEntry(
        asignatura=asignatura,
        curso=curso,
        aula=aula,
        profesor=profesor,
        dia=dia,
        hora=hora,
    )

    return entrada, profesor, es_nuevo


def _obtener_o_crear_profesor(nombre_raw: str, cache: dict) -> tuple:
    """
    Busca el profesor por el nombre literal del fichero.

    La cache es simple, pero evita muchas consultas repetidas porque un mismo
    profesor aparece decenas de veces en el horario.
    """
    if nombre_raw in cache:
        return cache[nombre_raw], False

    profesor, creado = Profesor.objects.get_or_create(nombre=nombre_raw)
    cache[nombre_raw] = profesor
    return profesor, creado
