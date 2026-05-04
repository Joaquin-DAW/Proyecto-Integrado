import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './reset-password.component.html',
})
export class ResetPasswordComponent implements OnInit {
  uid = '';
  token = '';
  form = { nueva_password: '', confirmar: '' };
  loading = false;
  error = '';
  mensaje = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private auth: AuthService,
  ) {}

  ngOnInit() {
    this.uid = this.route.snapshot.queryParamMap.get('uid') ?? '';
    this.token = this.route.snapshot.queryParamMap.get('token') ?? '';
    if (!this.uid || !this.token) {
      this.error = 'El enlace de recuperacion no es valido.';
    }
  }

  get passwordsNoCoinciden(): boolean {
    return !!this.form.nueva_password && !!this.form.confirmar &&
      this.form.nueva_password !== this.form.confirmar;
  }

  onSubmit() {
    if (!this.uid || !this.token || this.passwordsNoCoinciden || !this.form.nueva_password) return;
    this.loading = true;
    this.error = '';
    this.mensaje = '';

    this.auth.resetPassword(this.uid, this.token, this.form.nueva_password).subscribe({
      next: res => {
        this.mensaje = res.mensaje;
        this.loading = false;
        setTimeout(() => this.router.navigate(['/login']), 1200);
      },
      error: (err) => {
        this.error = err?.error?.error ?? 'No se pudo cambiar la contraseña.';
        this.loading = false;
      },
    });
  }
}
