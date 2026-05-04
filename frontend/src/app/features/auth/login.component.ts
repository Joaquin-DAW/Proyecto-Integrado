import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.component.html',
})
export class LoginComponent {
  email = '';
  password = '';
  error = '';
  loading = false;

  constructor(private auth: AuthService, private router: Router) {}

  onSubmit() {
    if (!this.email || !this.password) return;
    this.loading = true;
    this.error = '';

    this.auth.login(this.email, this.password).subscribe({
      next: () => {
        const user = this.auth.currentUser();
        const destino = user?.must_change_password && user.role === 'PROFESORADO'
          ? '/change-password'
          : '/dashboard';
        this.router.navigate([destino]);
      },
      error: () => {
        this.error = 'Credenciales incorrectas. Comprueba tu email y contraseña.';
        this.loading = false;
      },
    });
  }
}
