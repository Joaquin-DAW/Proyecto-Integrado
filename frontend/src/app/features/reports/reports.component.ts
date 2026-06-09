import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReportsService } from '../../core/services/reports.service';
import { ParteAusencias } from '../../core/models';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './reports.component.html',
})
export class ReportsComponent implements OnInit {
  partes: ParteAusencias[] = [];
  loading = true;
  generando = false;
  enviandoId: number | null = null;
  error = '';
  exito = '';

  form = { fecha: '', tipo: 'G' as ParteAusencias['tipo'] };

  constructor(private reportsService: ReportsService) {}

  ngOnInit() {
    this.cargar();
  }

  cargar() {
    this.loading = true;
    this.reportsService.listar().subscribe({
      next: data => {
        this.partes = data;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudieron cargar los partes.';
        this.loading = false;
      },
    });
  }

  generar() {
    if (!this.form.fecha) return;
    this.generando = true;
    this.error = '';
    this.exito = '';

    this.reportsService.generar(this.form.fecha, this.form.tipo).subscribe({
      next: () => {
        this.exito = `Parte ${this.tipoLabel(this.form.tipo)} generado correctamente.`;
        this.generando = false;
        this.cargar();
      },
      error: err => {
        this.error = err?.error?.error ?? 'Error al generar el parte.';
        this.generando = false;
      },
    });
  }

  tipoLabel(tipo: ParteAusencias['tipo']) {
    if (tipo === 'G') return 'IES completo';
    return `Módulo ${tipo}`;
  }

  tipoBadgeClass(tipo: ParteAusencias['tipo']) {
    if (tipo === 'G') return 'bg-dark';
    if (tipo === 'A') return 'bg-primary';
    return 'bg-info';
  }

  enviar(parte: ParteAusencias) {
    this.enviandoId = parte.id;
    this.error = '';
    this.exito = '';

    this.reportsService.enviar(parte.id).subscribe({
      next: res => {
        this.exito = res.mensaje;
        this.enviandoId = null;
      },
      error: err => {
        this.error = err?.error?.error ?? 'Error al enviar el parte por email.';
        this.enviandoId = null;
      },
    });
  }
}
