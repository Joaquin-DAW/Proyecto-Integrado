import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AbsenceService } from '../../core/services/absence.service';
import { Ausencia } from '../../core/models';

@Component({
  selector: 'app-all-absences',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './all-absences.component.html',
})
export class AllAbsencesComponent implements OnInit {
  ausencias: Ausencia[] = [];
  loading = true;
  filtroFecha = '';
  error = '';

  constructor(private absenceService: AbsenceService) {}

  ngOnInit() {
    this.cargar();
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
}
