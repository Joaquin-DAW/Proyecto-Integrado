import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './forgot-password.component.html',
})
export class ForgotPasswordComponent {
  email = '';
  loading = false;
  error = '';
  mensaje = '';

  constructor(private auth: AuthService) {}

  onSubmit() {
    if (!this.email) return;
    this.loading = true;
    this.error = '';
    this.mensaje = '';

    this.auth.requestPasswordReset(this.email).subscribe({
      next: res => {
        this.mensaje = res.mensaje;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudo solicitar la recuperación de contraseña.';
        this.loading = false;
      },
    });
  }
}
