"""
Construccion del PDF de ausencias.

El PDF mezcla guardias y ausencias por tramo. Se puede generar para todo el IES
o, si hace falta, solo para el modulo A o B.
"""
import datetime
import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.absences.models import Ausencia
from apps.schedules.models import HorarioEntry

COLOR_CABECERA = colors.HexColor('#2c3e50')
COLOR_FILA_PAR = colors.HexColor('#f2f2f2')
COLOR_RECREO = colors.HexColor('#e8e8e8')
COLOR_JUSTIFICADA = colors.HexColor('#d4edda')
COLOR_NO_JUST = colors.HexColor('#f8d7da')

DIAS_ES = {0: 'Lunes', 1: 'Martes', 2: 'Miercoles', 3: 'Jueves', 4: 'Viernes'}
RECREOS = {4, 11}

HORAS_RANGO = {
    1: '8:15-9:15', 2: '9:15-10:15', 3: '10:15-11:15',
    4: '11:15-11:45', 5: '11:45-12:45', 6: '12:45-13:45',
    7: '13:45-14:45', 8: '15:15-16:15', 9: '16:15-17:15',
    10: '17:15-18:15', 11: '18:15-18:45', 12: '18:45-19:45',
    13: '19:45-20:45', 14: '20:45-21:45',
}


def generar_pdf(fecha: datetime.date, tipo: str) -> bytes:
    ausencias = _cargar_ausencias_de_modulo(fecha, tipo)
    guardias = _cargar_guardias_de_modulo(fecha, tipo)
    profesores_ausentes = {a.horario_entry.profesor_id for a in ausencias}

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    story += _bloque_cabecera(fecha, tipo, styles)
    story.append(Spacer(1, 0.4 * cm))

    tramos_con_datos = _tramos_con_datos(ausencias, guardias)

    if not tramos_con_datos:
        story.append(Paragraph(
            'No hay ausencias ni guardias registradas para esta fecha.',
            ParagraphStyle('info', parent=styles['Normal'], textColor=colors.grey),
        ))
    else:
        story.append(_tabla_parte(tramos_con_datos, styles, profesores_ausentes))
        story.append(Spacer(1, 0.4 * cm))
        story.append(_fila_resumen(ausencias, styles))

    story.append(Spacer(1, 0.8 * cm))
    story.append(_pie(styles))

    doc.build(story)
    return buffer.getvalue()


# Reglas para decidir en que parte aparece cada fila.

def _asignar_modulo(aula: str) -> str:
    """
    Usa el primer caracter del aula como pista del modulo.

    Es una regla practica para el fichero actual; si el centro entrega una tabla
    oficial de modulos, este seria el sitio a cambiar.
    """
    if not aula or not aula.strip():
        return 'AMBOS'
    primer = aula.strip()[0]
    if primer == '1':
        return 'A'
    if primer == '2':
        return 'B'
    return 'AMBOS'


def _asignar_modulo_guardia(entry: HorarioEntry) -> str:
    """
    Algunas guardias vienen como GUARDIA A o GUARDIA B en el campo curso.
    Cuando no aparece esa pista, se usa el aula como criterio aproximado.
    """
    curso = (entry.curso or '').upper()
    texto_guardia = f"{entry.asignatura or ''} {curso}".upper()
    if 'BIBLIOTECA' in texto_guardia:
        return 'A'
    if 'GUARDIA A' in curso:
        return 'A'
    if 'GUARDIA B' in curso:
        return 'B'
    return _asignar_modulo(entry.aula)


def _etiqueta_modulo_guardia(entry: HorarioEntry) -> str:
    modulo = _asignar_modulo_guardia(entry)
    if modulo in ('A', 'B'):
        return f'Modulo {modulo}'
    return 'General'


def _cargar_ausencias_de_modulo(fecha: datetime.date, tipo: str) -> list:
    todas = (
        Ausencia.objects
        .filter(fecha=fecha)
        .select_related('horario_entry__profesor')
        .order_by('horario_entry__hora', 'horario_entry__profesor__nombre')
    )
    if tipo == 'G':
        return list(todas)
    return [a for a in todas if _asignar_modulo(a.horario_entry.aula) in (tipo, 'AMBOS')]


def _cargar_guardias_de_modulo(fecha: datetime.date, tipo: str) -> list:
    """
    Carga las guardias del dia. En el fichero se reconocen porque la asignatura
    contiene GUARDIA, incluyendo recreo, biblioteca y convivencia.
    """
    dia = _dia_codigo(fecha)
    if not dia:
        return []

    qs = (
        HorarioEntry.objects
        .filter(dia=dia, asignatura__icontains='GUARDIA')
        .select_related('profesor')
        .order_by('hora', 'curso', 'profesor__nombre')
    )
    if tipo == 'G':
        return list(qs)
    return [e for e in qs if _asignar_modulo_guardia(e) in (tipo, 'AMBOS')]


def _dia_codigo(fecha: datetime.date) -> str:
    return {0: 'L', 1: 'M', 2: 'X', 3: 'J', 4: 'V'}.get(fecha.weekday(), '')


def _tramos_con_datos(ausencias: list, guardias: list) -> dict:
    """
    Junta ausencias y guardias por tramo para pintar una sola tabla.
    Solo se incluyen horas con algo que mostrar.
    """
    tramos: dict = {}

    for ausencia in ausencias:
        hora = ausencia.horario_entry.hora
        tramos.setdefault(hora, {'ausencias': [], 'guardias': []})
        tramos[hora]['ausencias'].append(ausencia)

    for guardia in guardias:
        hora = guardia.hora
        tramos.setdefault(hora, {'ausencias': [], 'guardias': []})
        tramos[hora]['guardias'].append(guardia)

    return dict(sorted(tramos.items()))


# Bloques de maquetacion del PDF.

def _bloque_cabecera(fecha: datetime.date, tipo: str, styles) -> list:
    dia_str = DIAS_ES.get(fecha.weekday(), '')
    fecha_str = f"{dia_str}, {fecha.strftime('%d/%m/%Y')}"
    titulo_parte = (
        'Parte comun de ausencias'
        if tipo == 'G'
        else f'Parte de ausencias - Modulo {tipo}'
    )

    titulo = ParagraphStyle(
        'titulo',
        parent=styles['Title'],
        fontSize=14,
        textColor=COLOR_CABECERA,
        spaceAfter=2,
    )
    sub = ParagraphStyle(
        'sub',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )
    return [
        Paragraph('IES Poligono Sur', titulo),
        Paragraph(titulo_parte, titulo),
        Paragraph(fecha_str, sub),
    ]


def _tabla_parte(tramos: dict, styles, profesores_ausentes: set) -> Table:
    small = ParagraphStyle('sm', parent=styles['Normal'], fontSize=7, leading=9)
    small_grey = ParagraphStyle(
        'smg',
        parent=styles['Normal'],
        fontSize=7,
        leading=9,
        textColor=colors.grey,
    )

    cabecera = [
        Paragraph('<b>Hora</b>', small),
        Paragraph('<b>Profesores de guardia</b>', small),
        Paragraph('<b>Profesores ausentes</b>', small),
        Paragraph('<b>Grupo</b>', small),
        Paragraph('<b>Aula</b>', small),
        Paragraph('<b>Just.</b>', small),
    ]
    filas = [cabecera]
    estilos = [
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_CABECERA),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]

    fila_idx = 1
    for hora, datos in tramos.items():
        es_recreo = hora in RECREOS
        ausencias = datos['ausencias']
        guardias = datos['guardias']

        rango = HORAS_RANGO.get(hora, '')
        label_hora = f"{hora}{'R' if es_recreo else ''}<br/>{escape(rango)}"

        texto_guardias = '<br/>'.join(
            _texto_guardia(guardia, profesores_ausentes) for guardia in guardias
        ) if guardias else '-'

        if ausencias:
            for i, ausencia in enumerate(ausencias):
                entry = ausencia.horario_entry
                just_color = COLOR_JUSTIFICADA if ausencia.justificada else COLOR_NO_JUST

                fila = [
                    Paragraph(label_hora if i == 0 else '', small),
                    Paragraph(texto_guardias if i == 0 else '', small),
                    Paragraph(_texto_ausencia(ausencia), small),
                    Paragraph(escape(entry.curso or '-'), small_grey),
                    Paragraph(escape(entry.aula or '-'), small_grey),
                    Paragraph('Si' if ausencia.justificada else 'No', small),
                ]
                filas.append(fila)
                estilos.append(('BACKGROUND', (5, fila_idx), (5, fila_idx), just_color))

                if es_recreo:
                    estilos.append(('BACKGROUND', (0, fila_idx), (1, fila_idx), COLOR_RECREO))
                elif fila_idx % 2 == 0:
                    estilos.append(('BACKGROUND', (0, fila_idx), (1, fila_idx), COLOR_FILA_PAR))

                fila_idx += 1
        else:
            fila = [
                Paragraph(label_hora, small),
                Paragraph(texto_guardias, small),
                Paragraph('Sin ausencias', small_grey),
                Paragraph('', small),
                Paragraph('', small),
                Paragraph('', small),
            ]
            filas.append(fila)
            if es_recreo:
                estilos.append(('BACKGROUND', (0, fila_idx), (-1, fila_idx), COLOR_RECREO))
            elif fila_idx % 2 == 0:
                estilos.append(('BACKGROUND', (0, fila_idx), (-1, fila_idx), COLOR_FILA_PAR))
            fila_idx += 1

    tabla = Table(
        filas,
        colWidths=[2 * cm, 6 * cm, 5.5 * cm, 4 * cm, 2 * cm, 1.5 * cm],
        repeatRows=1,
    )
    tabla.setStyle(TableStyle(estilos))
    return tabla


def _texto_guardia(guardia: HorarioEntry, profesores_ausentes: set) -> str:
    estado = ' (ausente)' if guardia.profesor_id in profesores_ausentes else ''
    detalle = guardia.curso or guardia.asignatura
    modulo = _etiqueta_modulo_guardia(guardia)
    return (
        f"{escape(guardia.profesor.nombre)}{estado} - "
        f"{escape(detalle)} [{escape(modulo)}]"
    )


def _texto_ausencia(ausencia: Ausencia) -> str:
    texto = escape(ausencia.horario_entry.profesor.nombre)
    if ausencia.tareas:
        texto += f"<br/><font color='grey'>Tareas: {escape(ausencia.tareas)}</font>"
    return texto


def _fila_resumen(ausencias: list, styles) -> Table:
    total = len(ausencias)
    justificadas = sum(1 for a in ausencias if a.justificada)
    no_justificadas = total - justificadas

    estilo = ParagraphStyle('res', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
    datos = [[
        Paragraph(f'Total ausencias: <b>{total}</b>', estilo),
        Paragraph(f'Justificadas: <b>{justificadas}</b>', estilo),
        Paragraph(f'No justificadas: <b>{no_justificadas}</b>', estilo),
    ]]
    tabla = Table(datos, colWidths=[6 * cm, 5 * cm, 5 * cm])
    tabla.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    return tabla


def _pie(styles) -> Paragraph:
    ahora = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
    return Paragraph(
        f'Generado automaticamente el {ahora} - Horarium - IES Poligono Sur',
        ParagraphStyle(
            'pie',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.grey,
            alignment=TA_CENTER,
        ),
    )
