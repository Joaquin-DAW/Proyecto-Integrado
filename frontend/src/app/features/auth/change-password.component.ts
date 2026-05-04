import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { UsersService } from '../../core/services/users.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './change-password.component.html',
})
export class ChangePasswordComponent {
  form = { password_actual: '', nueva_password: '', confirmar: '' };
  guardando = false;
  error = '';
  exito = '';

  constructor(public auth: AuthService, private usersService: UsersService, private router: Router) {}

  get passwordsNoCoinciden(): boolean {
    return !!this.form.nueva_password && !!this.form.confirmar &&
      this.form.nueva_password !== this.form.confirmar;
  }

  onSubmit() {
    if (this.passwordsNoCoinciden) return;
    this.guardando = true;
    this.error = '';
    this.exito = '';

    this.usersService.cambiarPassword(this.form.password_actual, this.form.nueva_password).subscribe({
      next: () => {
        const eraCambioForzado = this.auth.currentUser()?.must_change_password ?? false;
        this.auth.clearMustChangePassword();
        this.exito = 'Contraseña actualizada correctamente.';
        this.guardando = false;
        this.form = { password_actual: '', nueva_password: '', confirmar: '' };
        if (eraCambioForzado) {
          setTimeout(() => this.router.navigate(['/dashboard']), 1500);
        }
      },
      error: (err) => {
        this.error = err?.error?.error ?? 'Error al cambiar la contraseña.';
        this.guardando = false;
      },
    });
  }
}
