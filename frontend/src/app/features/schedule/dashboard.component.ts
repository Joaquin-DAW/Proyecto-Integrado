import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ScheduleService } from '../../core/services/schedule.service';
import { HorarioEntry } from '../../core/models';

const DIAS = [
  { code: 'L', label: 'Lunes' },
  { code: 'M', label: 'Martes' },
  { code: 'X', label: 'Miércoles' },
  { code: 'J', label: 'Jueves' },
  { code: 'V', label: 'Viernes' },
];

const HORAS = Array.from({ length: 14 }, (_, i) => i + 1);
const RECREOS = new Set([4, 11]);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
})
export class DashboardComponent implements OnInit {
  dias = DIAS;
  horas = HORAS;
  recreos = RECREOS;
  horario: HorarioEntry[] = [];
  loading = true;
  error = '';

  constructor(private scheduleService: ScheduleService) {}

  ngOnInit() {
    this.scheduleService.miHorario().subscribe({
      next: data => {
        this.horario = data;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudo cargar el horario.';
        this.loading = false;
      },
    });
  }

  getEntrada(dia: string, hora: number): HorarioEntry | undefined {
    return this.horario.find(e => e.dia === dia && e.hora === hora);
  }
}
