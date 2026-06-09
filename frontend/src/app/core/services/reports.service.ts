import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { ParteAusencias } from '../models';

@Injectable({ providedIn: 'root' })
export class ReportsService {
  private url = `${environment.apiUrl}/reports`;

  constructor(private http: HttpClient) {}

  listar(params?: { fecha?: string; tipo?: string }) {
    let httpParams = new HttpParams();
    if (params?.fecha) httpParams = httpParams.set('fecha', params.fecha);
    if (params?.tipo) httpParams = httpParams.set('tipo', params.tipo);
    return this.http.get<ParteAusencias[]>(`${this.url}/`, { params: httpParams });
  }

  generar(fecha: string, tipo: 'G' | 'A' | 'B') {
    return this.http.post<ParteAusencias>(`${this.url}/generar/`, { fecha, tipo });
  }

  enviar(id: number) {
    return this.http.post<{ mensaje: string }>(`${this.url}/${id}/enviar/`, {});
  }
}
