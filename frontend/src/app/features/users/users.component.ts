import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UsersService } from '../../core/services/users.service';
import { AuthService } from '../../core/services/auth.service';
import { Profesor, Usuario } from '../../core/models';

interface CuentaDraft {
  email: string;
  role: Usuario['role'];
  is_active: boolean;
}

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './users.component.html',
})
export class UsersComponent implements OnInit {
  profesores: Profesor[] = [];
  drafts: Record<number, CuentaDraft> = {};
  loading = true;
  guardandoId: number | null = null;
  eliminandoId: number | null = null;
  error = '';
  exito = '';
  filtroBusqueda = '';
  filtroEstado: 'TODOS' | 'CON_CUENTA' | 'SIN_CUENTA' | 'DIRECTIVO' = 'TODOS';

  // Se rellena solo al crear cuenta, porque la contraseña temporal no se guarda visible.
  credencialesNuevas: { email: string; password: string } | null = null;

  constructor(
    private usersService: UsersService,
    public auth: AuthService,
  ) {}

  ngOnInit() {
    this.cargar();
  }

  cargar() {
    this.loading = true;
    this.usersService.listarProfesores().subscribe({
      next: data => {
        this.profesores = data;
        this.prepararBorradores();
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudieron cargar los profesores.';
        this.loading = false;
      },
    });
  }

  get profesoresFiltrados(): Profesor[] {
    const q = this.filtroBusqueda.trim().toLowerCase();

    return this.profesores.filter(profesor => {
      const coincideTexto = !q
        || profesor.nombre.toLowerCase().includes(q)
        || profesor.email_institucional.toLowerCase().includes(q)
        || profesor.user?.email.toLowerCase().includes(q);

      if (!coincideTexto) return false;
      if (this.filtroEstado === 'CON_CUENTA') return !!profesor.user;
      if (this.filtroEstado === 'SIN_CUENTA') return !profesor.user;
      if (this.filtroEstado === 'DIRECTIVO') {
        return profesor.user?.role === 'EQUIPO_DIRECTIVO';
      }
      return true;
    });
  }

  get totalConCuenta() {
    return this.profesores.filter(p => p.user).length;
  }

  get totalDirectivos() {
    return this.profesores.filter(p => p.user?.role === 'EQUIPO_DIRECTIVO').length;
  }

  crearCuenta(profesor: Profesor) {
    if (!confirm(`¿Crear cuenta para ${profesor.nombre}? Se generará una contraseña temporal.`)) return;
    this.error = '';
    this.exito = '';

    this.usersService.crearCuenta(profesor.id).subscribe({
      next: res => {
        this.credencialesNuevas = {
          email: res.usuario.email,
          password: res.password_temporal,
        };
        this.exito = `Cuenta creada para ${profesor.nombre}.`;
        this.cargar();
      },
      error: err => (this.error = err?.error?.error ?? 'Error al crear la cuenta.'),
    });
  }

  guardarCuenta(profesor: Profesor) {
    if (!profesor.user) return;
    const draft = this.drafts[profesor.user.id];
    if (!draft) return;
    if (
      this.esUsuarioActual(profesor)
      && (draft.role !== profesor.user.role || draft.is_active !== profesor.user.is_active)
    ) {
      this.error = 'No puedes cambiar tu propio rol ni desactivar tu cuenta desde esta pantalla.';
      return;
    }

    this.guardandoId = profesor.user.id;
    this.error = '';
    this.exito = '';

    this.usersService.actualizarUsuario(profesor.user.id, draft).subscribe({
      next: usuario => {
        profesor.user = usuario;
        profesor.tiene_cuenta = true;
        this.drafts[usuario.id] = this.crearDraft(usuario);
        this.guardandoId = null;
        this.exito = `Cuenta actualizada: ${usuario.email}`;
      },
      error: err => {
        this.error = err?.error?.error ?? 'No se pudo actualizar la cuenta.';
        this.guardandoId = null;
      },
    });
  }

  eliminarCuenta(profesor: Profesor) {
    if (!profesor.user) return;
    if (!confirm(`¿Eliminar la cuenta de ${profesor.nombre}? El profesor seguirá en el horario.`)) return;

    this.eliminandoId = profesor.user.id;
    this.error = '';
    this.exito = '';

    this.usersService.eliminarUsuario(profesor.user.id).subscribe({
      next: () => {
        delete this.drafts[profesor.user!.id];
        profesor.user = null;
        profesor.tiene_cuenta = false;
        this.eliminandoId = null;
        this.exito = `Cuenta eliminada para ${profesor.nombre}.`;
      },
      error: err => {
        this.error = err?.error?.error ?? 'No se pudo eliminar la cuenta.';
        this.eliminandoId = null;
      },
    });
  }

  haCambiado(profesor: Profesor) {
    if (!profesor.user) return false;
    const draft = this.drafts[profesor.user.id];
    return !!draft && (
      draft.email !== profesor.user.email
      || draft.role !== profesor.user.role
      || draft.is_active !== profesor.user.is_active
    );
  }

  esUsuarioActual(profesor: Profesor) {
    return profesor.user?.id === this.auth.currentUser()?.id;
  }

  roleLabel(role: Usuario['role']) {
    return role === 'EQUIPO_DIRECTIVO' ? 'Equipo directivo' : 'Profesorado';
  }

  cerrarModal() {
    this.credencialesNuevas = null;
  }

  private prepararBorradores() {
    this.drafts = {};
    for (const profesor of this.profesores) {
      if (profesor.user) {
        this.drafts[profesor.user.id] = this.crearDraft(profesor.user);
      }
    }
  }

  private crearDraft(usuario: Usuario): CuentaDraft {
    return {
      email: usuario.email,
      role: usuario.role,
      is_active: usuario.is_active,
    };
  }
}
