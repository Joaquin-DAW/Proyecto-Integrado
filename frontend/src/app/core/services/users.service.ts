import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Profesor, Usuario } from '../models';

@Injectable({ providedIn: 'root' })
export class UsersService {
  private url = `${environment.apiUrl}/users`;

  constructor(private http: HttpClient) {}

  listarProfesores() {
    return this.http.get<Profesor[]>(`${this.url}/profesores/`);
  }

  crearCuenta(profesorId: number) {
    return this.http.post<{ usuario: Usuario; password_temporal: string }>(
      `${this.url}/profesores/${profesorId}/crear-cuenta/`,
      {},
    );
  }

  eliminarUsuario(userId: number) {
    return this.http.delete(`${this.url}/${userId}/eliminar/`);
  }

  cambiarPassword(passwordActual: string, nuevaPassword: string) {
    return this.http.post(`${this.url}/me/cambiar-password/`, {
      password_actual: passwordActual,
      nueva_password: nuevaPassword,
    });
  }
}
