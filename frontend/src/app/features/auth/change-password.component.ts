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
  mostrarPasswords = false;
  guardando = false;
  error = '';
  exito = '';

  constructor(public auth: AuthService, private usersService: UsersService, private router: Router) {}

  get passwordsNoCoinciden(): boolean {
    return !!this.form.nueva_password && !!this.form.confirmar &&
      this.form.nueva_password !== this.form.confirmar;
  }

  get passwordChecks() {
    const password = this.form.nueva_password;
    return [
      { texto: 'Mínimo 8 caracteres', ok: password.length >= 8 },
      { texto: 'Al menos una letra', ok: /[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]/.test(password) },
      { texto: 'Al menos un número', ok: /\d/.test(password) },
      { texto: 'Al menos un carácter especial', ok: /[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9\s]/.test(password) },
    ];
  }

  get passwordValida(): boolean {
    return this.passwordChecks.every(regla => regla.ok);
  }

  onSubmit() {
    if (this.passwordsNoCoinciden || !this.passwordValida) return;
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
        this.mostrarPasswords = false;
        if (eraCambioForzado) {
          setTimeout(() => this.router.navigate(['/dashboard']), 1500);
        }
      },
      error: (err) => {
        this.error = err?.error?.error
          ?? err?.error?.nueva_password?.[0]
          ?? 'Error al cambiar la contraseña.';
        this.guardando = false;
      },
    });
  }
}
