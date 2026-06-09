import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ScheduleService, FiltrosHorario } from '../../core/services/schedule.service';
import { HorarioEntry } from '../../core/models';

const DIAS = [
  { code: 'L', label: 'Lunes' },
  { code: 'M', label: 'Martes' },
  { code: 'X', label: 'Miércoles' },
  { code: 'J', label: 'Jueves' },
  { code: 'V', label: 'Viernes' },
];

@Component({
  selector: 'app-schedule-search',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './schedule-search.component.html',
})
export class ScheduleSearchComponent {
  dias = DIAS;
  filtros: FiltrosHorario = {
    profesor_nombre: '',
    dia: '',
    grupo: '',
    asignatura: '',
    aula: '',
  };

  resultados: HorarioEntry[] = [];
  loading = false;
  buscado = false;
  error = '';

  constructor(private scheduleService: ScheduleService) {}

  buscar() {
    // Sin ningun filtro la consulta devolveria demasiado horario de golpe.
    const hayFiltro = Object.values(this.filtros).some(v => String(v ?? '').trim());
    if (!hayFiltro) return;

    this.loading = true;
    this.error = '';
    this.buscado = false;

    this.scheduleService.buscar(this.filtros).subscribe({
      next: data => {
        this.resultados = data;
        this.loading = false;
        this.buscado = true;
      },
      error: () => {
        this.error = 'Error al realizar la búsqueda.';
        this.loading = false;
      },
    });
  }

  limpiar() {
    this.filtros = {
      profesor_nombre: '',
      dia: '',
      grupo: '',
      asignatura: '',
      aula: '',
    };
    this.resultados = [];
    this.buscado = false;
  }

  getDiaLabel(code: string): string {
    return this.dias.find(d => d.code === code)?.label ?? code;
  }
}
