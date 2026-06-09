import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ScheduleService } from '../../core/services/schedule.service';
import { AbsenceService } from '../../core/services/absence.service';
import { AuthService } from '../../core/services/auth.service';
import { Ausencia, GuardiaPanel, HorarioEntry, PanelDiario } from '../../core/models';

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
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.component.html',
})
export class DashboardComponent implements OnInit, OnDestroy {
  dias = DIAS;
  horas = HORAS;
  recreos = RECREOS;
  horario: HorarioEntry[] = [];
  panel: PanelDiario | null = null;
  fechaPanel = this.getTodayInputValue();
  isDireccion = false;
  loading = true;
  refreshing = false;
  ultimaActualizacion = '';
  error = '';
  private refreshTimer: ReturnType<typeof setInterval> | null = null;

  constructor(
    private scheduleService: ScheduleService,
    private absenceService: AbsenceService,
    private authService: AuthService,
  ) {}

  ngOnInit() {
    this.isDireccion = this.authService.isEquipoDireccion();
    if (this.isDireccion) {
      this.cargarPanel(true);
      this.refreshTimer = setInterval(() => this.cargarPanel(false), 60000);
      return;
    }

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

  ngOnDestroy() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
  }

  cargarPanel(mostrarCarga = false) {
    if (mostrarCarga || !this.panel) {
      this.loading = true;
    } else {
      this.refreshing = true;
    }
    this.error = '';

    this.absenceService.panel(this.fechaPanel).subscribe({
      next: data => {
        this.panel = data;
        this.ultimaActualizacion = this.getCurrentTimeValue();
        this.loading = false;
        this.refreshing = false;
      },
      error: () => {
        this.error = 'No se pudo cargar el panel diario.';
        this.loading = false;
        this.refreshing = false;
      },
    });
  }

  cambiarFechaPanel() {
    this.cargarPanel(true);
  }

  getEntrada(dia: string, hora: number): HorarioEntry | undefined {
    return this.horario.find(e => e.dia === dia && e.hora === hora);
  }

  guardiasPorHora(hora: number): GuardiaPanel[] {
    return this.panel?.guardias.filter(g => g.hora === hora) ?? [];
  }

  ausenciasPorHora(hora: number): Ausencia[] {
    return this.panel?.ausencias.filter(a => a.hora === hora) ?? [];
  }

  moduloClass(modulo: GuardiaPanel['modulo']): string {
    if (modulo === 'A') return 'bg-primary';
    if (modulo === 'B') return 'bg-success';
    return 'bg-secondary';
  }

  private getTodayInputValue(): string {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }

  private getCurrentTimeValue(): string {
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, '0');
    const mm = String(now.getMinutes()).padStart(2, '0');
    return `${hh}:${mm}`;
  }
}
