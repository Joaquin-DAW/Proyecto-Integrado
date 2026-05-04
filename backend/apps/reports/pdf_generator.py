"""
Construccion del PDF de ausencias.

El diseño sigue el modelo del centro: por cada tramo aparecen primero los
profesores de guardia y despues las ausencias con grupo, aula y justificacion.

La separacion A/B se hace de momento por el aula:
- aulas que empiezan por 1: modulo A
- aulas que empiezan por 2: modulo B
- aula vacia o codigo especial: se muestra en los dos
"""
import io
import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from apps.absences.models import Ausencia
from apps.schedules.models import HorarioEntry

COLOR_CABECERA     = colors.HexColor('#2c3e50')
COLOR_FILA_PAR     = colors.HexColor('#f2f2f2')
COLOR_RECREO       = colors.HexColor('#e8e8e8')
COLOR_JUSTIFICADA  = colors.HexColor('#d4edda')
COLOR_NO_JUST      = colors.HexColor('#f8d7da')

DIAS_ES = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes'}
RECREOS = {4, 11}

HORAS_RANGO = {
    1: '8:15–9:15',   2: '9:15–10:15',  3: '10:15–11:15',
    4: '11:15–11:45', 5: '11:45–12:45', 6: '12:45–13:45',
    7: '13:45–14:45', 8: '15:15–16:15', 9: '16:15–17:15',
    10: '17:15–18:15', 11: '18:15–18:45', 12: '18:45–19:45',
    13: '19:45–20:45', 14: '20:45–21:45',
}


def generar_pdf(fecha: datetime.date, tipo: str) -> bytes:
    ausencias  = _cargar_ausencias_de_modulo(fecha, tipo)
    guardias   = _cargar_guardias_de_modulo(fecha, tipo)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm,  bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    story += _bloque_cabecera(fecha, tipo, styles)
    story.append(Spacer(1, 0.4 * cm))

    tramos_con_datos = _tramos_con_datos(ausencias, guardias)

    if not tramos_con_datos:
        story.append(Paragraph(
            'No hay ausencias ni guardias registradas para este módulo.',
            ParagraphStyle('info', parent=styles['Normal'], textColor=colors.grey),
        ))
    else:
        story.append(_tabla_parte(tramos_con_datos, styles))
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


def _cargar_ausencias_de_modulo(fecha: datetime.date, tipo: str) -> list:
    todas = (
        Ausencia.objects
        .filter(fecha=fecha)
        .select_related('horario_entry__profesor')
        .order_by('horario_entry__hora', 'horario_entry__profesor__nombre')
    )
    return [a for a in todas if _asignar_modulo(a.horario_entry.aula) in (tipo, 'AMBOS')]


def _cargar_guardias_de_modulo(fecha: datetime.date, tipo: str) -> list:
    """
    Carga las guardias del dia y deja solo las que entran en el modulo pedido.
    En el fichero se reconocen porque la asignatura contiene GUARDIA.
    """
    dia = _dia_codigo(fecha)
    if not dia:
        return []

    qs = (
        HorarioEntry.objects
        .filter(dia=dia, asignatura__icontains='GUARDIA')
        .select_related('profesor')
        .order_by('hora', 'profesor__nombre')
    )
    return [e for e in qs if _asignar_modulo(e.aula) in (tipo, 'AMBOS')]


def _dia_codigo(fecha: datetime.date) -> str:
    return {0: 'L', 1: 'M', 2: 'X', 3: 'J', 4: 'V'}.get(fecha.weekday(), '')


def _tramos_con_datos(ausencias: list, guardias: list) -> dict:
    """
    Junta ausencias y guardias por tramo para pintar una sola tabla.
    Solo se incluyen horas con algo que mostrar.
    """
    tramos: dict = {}

    for a in ausencias:
        h = a.horario_entry.hora
        tramos.setdefault(h, {'ausencias': [], 'guardias': []})
        tramos[h]['ausencias'].append(a)

    for g in guardias:
        h = g.hora
        tramos.setdefault(h, {'ausencias': [], 'guardias': []})
        tramos[h]['guardias'].append(g)

    return dict(sorted(tramos.items()))


# Bloques de maquetacion del PDF.

def _bloque_cabecera(fecha: datetime.date, tipo: str, styles) -> list:
    dia_str  = DIAS_ES.get(fecha.weekday(), '')
    fecha_str = f"{dia_str}, {fecha.strftime('%d/%m/%Y')}"

    titulo = ParagraphStyle(
        'titulo', parent=styles['Title'],
        fontSize=14, textColor=COLOR_CABECERA, spaceAfter=2,
    )
    sub = ParagraphStyle(
        'sub', parent=styles['Normal'],
        fontSize=10, textColor=colors.grey, alignment=TA_CENTER,
    )
    return [
        Paragraph('IES Polígono Sur', titulo),
        Paragraph(f'Parte de ausencias — Módulo {tipo}', titulo),
        Paragraph(fecha_str, sub),
    ]


def _tabla_parte(tramos: dict, styles) -> Table:
    small = ParagraphStyle('sm', parent=styles['Normal'], fontSize=7, leading=9)
    small_grey = ParagraphStyle('smg', parent=styles['Normal'], fontSize=7, leading=9,
                                textColor=colors.grey)

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
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('ALIGN',      (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE',   (0, 0), (-1, -1), 7),
        ('GRID',       (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING',   (0, 0), (-1, -1), 4),
    ]

    fila_idx = 1
    for hora, datos in tramos.items():
        es_recreo = hora in RECREOS
        ausencias = datos['ausencias']
        guardias  = datos['guardias']

        # Etiqueta visible del tramo, por ejemplo: "4R 11:15-11:45".
        rango = HORAS_RANGO.get(hora, '')
        label_hora = f"{hora}{'R' if es_recreo else ''}\n{rango}"

        # En una celda del PDF queda mas claro si cada guardia va en su linea.
        texto_guardias = '\n'.join(
            g.profesor.nombre for g in guardias
        ) if guardias else '—'

        if ausencias:
            for i, aus in enumerate(ausencias):
                entry = aus.horario_entry
                just_color = COLOR_JUSTIFICADA if aus.justificada else COLOR_NO_JUST

                fila = [
                    Paragraph(label_hora if i == 0 else '', small),
                    Paragraph(texto_guardias if i == 0 else '', small),
                    Paragraph(entry.profesor.nombre, small),
                    Paragraph(entry.curso or '—', small_grey),
                    Paragraph(entry.aula  or '—', small_grey),
                    Paragraph('Sí' if aus.justificada else 'No', small),
                ]
                filas.append(fila)
                estilos.append(('BACKGROUND', (5, fila_idx), (5, fila_idx), just_color))

                if es_recreo:
                    estilos.append(('BACKGROUND', (0, fila_idx), (1, fila_idx), COLOR_RECREO))
                elif fila_idx % 2 == 0:
                    estilos.append(('BACKGROUND', (0, fila_idx), (1, fila_idx), COLOR_FILA_PAR))

                fila_idx += 1
        else:
            # Hay guardias asignadas, pero ese tramo no tiene ausentes.
            fila = [
                Paragraph(label_hora, small),
                Paragraph(texto_guardias, small),
                Paragraph('Sin ausencias', small_grey),
                Paragraph('', small), Paragraph('', small), Paragraph('', small),
            ]
            filas.append(fila)
            if es_recreo:
                estilos.append(('BACKGROUND', (0, fila_idx), (-1, fila_idx), COLOR_RECREO))
            elif fila_idx % 2 == 0:
                estilos.append(('BACKGROUND', (0, fila_idx), (-1, fila_idx), COLOR_FILA_PAR))
            fila_idx += 1

    tabla = Table(
        filas,
        colWidths=[2*cm, 6*cm, 5.5*cm, 4*cm, 2*cm, 1.5*cm],
        repeatRows=1,
    )
    tabla.setStyle(TableStyle(estilos))
    return tabla


def _fila_resumen(ausencias: list, styles) -> Table:
    total = len(ausencias)
    justificadas    = sum(1 for a in ausencias if a.justificada)
    no_justificadas = total - justificadas

    estilo = ParagraphStyle('res', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
    datos = [[
        Paragraph(f'Total ausencias: <b>{total}</b>', estilo),
        Paragraph(f'Justificadas: <b>{justificadas}</b>', estilo),
        Paragraph(f'No justificadas: <b>{no_justificadas}</b>', estilo),
    ]]
    t = Table(datos, colWidths=[6*cm, 5*cm, 5*cm])
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    return t


def _pie(styles) -> Paragraph:
    ahora = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
    return Paragraph(
        f'Generado automáticamente el {ahora} · Horarium — IES Polígono Sur',
        ParagraphStyle('pie', parent=styles['Normal'], fontSize=7,
                       textColor=colors.grey, alignment=TA_CENTER),
    )
