import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { LoginResponse, Usuario } from '../models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly ACCESS_KEY = 'horarium_access';
  private readonly REFRESH_KEY = 'horarium_refresh';
  private readonly USER_KEY = 'horarium_user';

  // Signal compartido: nav, guards y pantallas leen siempre el mismo usuario.
  currentUser = signal<Usuario | null>(this.loadUser());

  constructor(private http: HttpClient, private router: Router) {}

  login(email: string, password: string) {
    return this.http
      .post<LoginResponse>(`${environment.apiUrl}/auth/login/`, { email, password })
      .pipe(
        tap(res => {
          localStorage.setItem(this.ACCESS_KEY, res.access);
          localStorage.setItem(this.REFRESH_KEY, res.refresh);
          localStorage.setItem(this.USER_KEY, JSON.stringify(res.usuario));
          this.currentUser.set(res.usuario);
        }),
      );
  }

  requestPasswordReset(email: string) {
    return this.http.post<{ mensaje: string }>(
      `${environment.apiUrl}/auth/password-reset/`,
      { email },
    );
  }

  resetPassword(uid: string, token: string, nuevaPassword: string) {
    return this.http.post<{ mensaje: string }>(
      `${environment.apiUrl}/auth/password-reset/confirm/`,
      { uid, token, nueva_password: nuevaPassword },
    );
  }

  logout() {
    localStorage.removeItem(this.ACCESS_KEY);
    localStorage.removeItem(this.REFRESH_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_KEY);
  }

  isLoggedIn(): boolean {
    return !!this.getAccessToken();
  }

  isEquipoDireccion(): boolean {
    return this.currentUser()?.role === 'EQUIPO_DIRECTIVO';
  }

  // Renueva el access token sin sacar al usuario de la sesion.
  refreshToken() {
    const refresh = this.getRefreshToken();
    return this.http
      .post<{ access: string }>(`${environment.apiUrl}/auth/refresh/`, { refresh })
      .pipe(
        tap(res => localStorage.setItem(this.ACCESS_KEY, res.access)),
      );
  }

  clearMustChangePassword() {
    const user = this.currentUser();
    if (user) {
      const updated = { ...user, must_change_password: false };
      localStorage.setItem(this.USER_KEY, JSON.stringify(updated));
      this.currentUser.set(updated);
    }
  }

  private loadUser(): Usuario | null {
    const raw = localStorage.getItem(this.USER_KEY);
    return raw ? JSON.parse(raw) : null;
  }
}
