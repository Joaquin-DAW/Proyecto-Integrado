import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { ParteAusencias } from '../models';

@Injectable({ providedIn: 'root' })
export class ReportsService {
  private url = `${environment.apiUrl}/reports`;

  constructor(private http: HttpClient) {}

  listar(params?: { fecha?: string; tipo?: string }) {
    let query = '';
    if (params?.fecha) query += `?fecha=${params.fecha}`;
    if (params?.tipo) query += `${query ? '&' : '?'}tipo=${params.tipo}`;
    return this.http.get<ParteAusencias[]>(`${this.url}/${query}`);
  }

  generar(fecha: string, tipo: 'A' | 'B') {
    return this.http.post<ParteAusencias>(`${this.url}/generar/`, { fecha, tipo });
  }

  enviar(id: number) {
    return this.http.post<{ mensaje: string }>(`${this.url}/${id}/enviar/`, {});
  }
}
