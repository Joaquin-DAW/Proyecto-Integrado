import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ImportScheduleResult, ScheduleService } from '../../core/services/schedule.service';

@Component({
  selector: 'app-import-schedule',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './import-schedule.component.html',
})
export class ImportScheduleComponent {
  archivo: File | null = null;
  importando = false;
  resultado: ImportScheduleResult | null = null;
  error = '';

  constructor(private scheduleService: ScheduleService) {}

  onFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    this.archivo = input.files?.[0] ?? null;
    this.resultado = null;
    this.error = '';
  }

  importar() {
    if (!this.archivo) return;
    this.importando = true;
    this.error = '';
    this.resultado = null;

    this.scheduleService.importar(this.archivo).subscribe({
      next: res => {
        this.resultado = res;
        this.importando = false;
        this.archivo = null;
      },
      error: (err) => {
        this.error = err?.error?.error ?? 'Error al importar el fichero.';
        this.importando = false;
      },
    });
  }
}
