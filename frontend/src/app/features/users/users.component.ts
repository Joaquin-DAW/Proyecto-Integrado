import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UsersService } from '../../core/services/users.service';
import { Profesor } from '../../core/models';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './users.component.html',
})
export class UsersComponent implements OnInit {
  profesores: Profesor[] = [];
  loading = true;
  error = '';
  filtroBusqueda = '';

  // Se rellena solo al crear cuenta, porque la contraseña temporal no se guarda visible.
  credencialesNuevas: { email: string; password: string } | null = null;

  constructor(private usersService: UsersService) {}

  ngOnInit() {
    this.cargar();
  }

  cargar() {
    this.loading = true;
    this.usersService.listarProfesores().subscribe({
      next: data => {
        this.profesores = data;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudieron cargar los profesores.';
        this.loading = false;
      },
    });
  }

  get profesoresFiltrados(): Profesor[] {
    if (!this.filtroBusqueda) return this.profesores;
    const q = this.filtroBusqueda.toLowerCase();
    return this.profesores.filter(p => p.nombre.toLowerCase().includes(q));
  }

  crearCuenta(profesor: Profesor) {
    if (!confirm(`¿Crear cuenta para ${profesor.nombre}? Se generará una contraseña temporal.`)) return;
    this.usersService.crearCuenta(profesor.id).subscribe({
      next: res => {
        this.credencialesNuevas = {
          email: res.usuario.email,
          password: res.password_temporal,
        };
        this.cargar();
      },
      error: (err) => alert(err?.error?.error ?? 'Error al crear la cuenta.'),
    });
  }

  cerrarModal() {
    this.credencialesNuevas = null;
  }
}
