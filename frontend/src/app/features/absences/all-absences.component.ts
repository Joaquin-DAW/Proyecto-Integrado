import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AbsenceService } from '../../core/services/absence.service';
import { ScheduleService } from '../../core/services/schedule.service';
import { UsersService } from '../../core/services/users.service';
import { Ausencia, HorarioEntry, Profesor } from '../../core/models';

interface TramoFormulario {
  hora: number;
  label: string;
}

@Component({
  selector: 'app-all-absences',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './all-absences.component.html',
})
export class AllAbsencesComponent implements OnInit {
  ausencias: Ausencia[] = [];
  profesores: Profesor[] = [];
  tramosProfesor: TramoFormulario[] = [];

  loading = true;
  cargandoHorario = false;
  guardando = false;
  filtroFecha = '';
  error = '';
  exito = '';

  form = {
    profesorId: null as number | null,
    fecha: '',
    horas: [] as number[],
    descripcion: '',
    tareas: '',
  };

  constructor(
    private absenceService: AbsenceService,
    private scheduleService: ScheduleService,
    private usersService: UsersService,
  ) {}

  ngOnInit() {
    this.cargar();
    this.cargarProfesores();
  }

  cargar() {
    this.loading = true;
    const params = this.filtroFecha ? { fecha: this.filtroFecha } : undefined;
    this.absenceService.listar(params).subscribe({
      next: data => {
        this.ausencias = data;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudieron cargar las ausencias.';
        this.loading = false;
      },
    });
  }

  cargarProfesores() {
    this.usersService.listarProfesores().subscribe({
      next: data => (this.profesores = data),
      error: () => (this.error = 'No se pudo cargar el profesorado.'),
    });
  }

  cargarHorarioProfesor() {
    this.form.horas = [];
    this.tramosProfesor = [];
    if (!this.form.profesorId || !this.form.fecha) return;

    const dia = this.diaCodigo(this.form.fecha);
    if (!dia) return;

    this.cargandoHorario = true;
    this.scheduleService.buscar({
      profesor_id: this.form.profesorId,
      dia,
    }).subscribe({
      next: data => {
        this.tramosProfesor = this.agruparTramos(data);
        this.cargandoHorario = false;
      },
      error: () => {
        this.error = 'No se pudo cargar el horario del profesor.';
        this.cargandoHorario = false;
      },
    });
  }

  registrarAusencia() {
    if (!this.form.profesorId || !this.form.fecha || this.form.horas.length === 0) return;

    this.guardando = true;
    this.error = '';
    this.exito = '';

    this.absenceService.crear({
      profesor_id: this.form.profesorId,
      fecha: this.form.fecha,
      horas: this.form.horas,
      descripcion: this.form.descripcion,
      tareas: this.form.tareas,
    }).subscribe({
      next: res => {
        this.exito = res.mensaje;
        this.form = { profesorId: null, fecha: '', horas: [], descripcion: '', tareas: '' };
        this.tramosProfesor = [];
        this.guardando = false;
        this.cargar();
      },
      error: err => {
        this.error = err?.error?.error ?? 'Error al registrar la ausencia.';
        this.guardando = false;
      },
    });
  }

  toggleHora(hora: number) {
    const idx = this.form.horas.indexOf(hora);
    if (idx === -1) this.form.horas.push(hora);
    else this.form.horas.splice(idx, 1);
  }

  isHoraSeleccionada(hora: number) {
    return this.form.horas.includes(hora);
  }

  toggleJustificada(ausencia: Ausencia) {
    const nuevo = !ausencia.justificada;
    this.absenceService.justificar(ausencia.id, nuevo).subscribe({
      next: updated => {
        ausencia.justificada = updated.justificada;
      },
      error: () => alert('Error al actualizar el estado.'),
    });
  }

  eliminar(id: number) {
    if (!confirm('¿Eliminar esta ausencia?')) return;
    this.absenceService.eliminar(id).subscribe({
      next: () => this.cargar(),
      error: () => alert('No se pudo eliminar la ausencia.'),
    });
  }

  limpiarFiltro() {
    this.filtroFecha = '';
    this.cargar();
  }

  private diaCodigo(fecha: string): string {
    const date = new Date(`${fecha}T12:00:00`);
    return ['', 'L', 'M', 'X', 'J', 'V'][date.getDay()] ?? '';
  }

  private agruparTramos(entries: HorarioEntry[]): TramoFormulario[] {
    const grupos = new Map<number, HorarioEntry[]>();
    for (const entry of entries) {
      const actuales = grupos.get(entry.hora) ?? [];
      actuales.push(entry);
      grupos.set(entry.hora, actuales);
    }

    return Array.from(grupos.entries())
      .sort(([a], [b]) => a - b)
      .map(([hora, tramoEntries]) => ({
        hora,
        label: `${hora} - ${this.resumenTramo(tramoEntries)}`,
      }));
  }

  private resumenTramo(entries: HorarioEntry[]) {
    return entries
      .map(entry => {
        const curso = entry.curso ? ` (${entry.curso})` : '';
        return `${entry.asignatura}${curso}`;
      })
      .join(' / ');
  }
}
