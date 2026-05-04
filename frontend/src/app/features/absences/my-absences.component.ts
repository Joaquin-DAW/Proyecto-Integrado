import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AbsenceService } from '../../core/services/absence.service';
import { ScheduleService } from '../../core/services/schedule.service';
import { Ausencia, HorarioEntry } from '../../core/models';

@Component({
  selector: 'app-my-absences',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './my-absences.component.html',
})
export class MyAbsencesComponent implements OnInit {
  ausencias: Ausencia[] = [];
  horario: HorarioEntry[] = [];

  loading = true;
  guardando = false;
  error = '';
  exito = '';

  // Estado del formulario de alta; las horas se limpian al cambiar de dia.
  form = {
    fecha: '',
    horas: [] as number[],
    descripcion: '',
  };

  constructor(
    private absenceService: AbsenceService,
    private scheduleService: ScheduleService,
  ) {}

  ngOnInit() {
    this.cargarDatos();
  }

  cargarDatos() {
    this.loading = true;
    this.absenceService.listar().subscribe({
      next: data => {
        this.ausencias = data;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudieron cargar las ausencias.';
        this.loading = false;
      },
    });
    this.scheduleService.miHorario().subscribe({
      next: data => (this.horario = data),
    });
  }

  // Del horario completo del profesor sacamos solo los tramos del dia elegido.
  get tramosDelDia(): HorarioEntry[] {
    if (!this.form.fecha) return [];
    const date = new Date(this.form.fecha + 'T12:00:00');
    const dayIndex = date.getDay(); // 0=domingo, 1=lunes...
    const diaCodes = ['', 'L', 'M', 'X', 'J', 'V'];
    const diaCode = diaCodes[dayIndex] ?? '';
    return this.horario
      .filter(e => e.dia === diaCode)
      .sort((a, b) => a.hora - b.hora);
  }

  toggleHora(hora: number) {
    const idx = this.form.horas.indexOf(hora);
    if (idx === -1) this.form.horas.push(hora);
    else this.form.horas.splice(idx, 1);
  }

  isHoraSeleccionada(hora: number) {
    return this.form.horas.includes(hora);
  }

  onFechaChange() {
    this.form.horas = [];
  }

  crearAusencia() {
    if (!this.form.fecha || this.form.horas.length === 0) return;
    this.guardando = true;
    this.error = '';
    this.exito = '';

    this.absenceService.crear({
      fecha: this.form.fecha,
      horas: this.form.horas,
      descripcion: this.form.descripcion,
    }).subscribe({
      next: () => {
        this.exito = 'Ausencia registrada correctamente.';
        this.form = { fecha: '', horas: [], descripcion: '' };
        this.guardando = false;
        this.cargarDatos();
      },
      error: (err) => {
        this.error = err?.error?.error ?? 'Error al registrar la ausencia.';
        this.guardando = false;
      },
    });
  }

  eliminar(id: number) {
    if (!confirm('¿Eliminar esta ausencia?')) return;
    this.absenceService.eliminar(id).subscribe({
      next: () => this.cargarDatos(),
      error: () => alert('No se pudo eliminar la ausencia.'),
    });
  }
}
