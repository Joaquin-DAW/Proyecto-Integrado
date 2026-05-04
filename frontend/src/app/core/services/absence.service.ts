import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Ausencia } from '../models';

@Injectable({ providedIn: 'root' })
export class AbsenceService {
  private url = `${environment.apiUrl}/absences`;

  constructor(private http: HttpClient) {}

  listar(params?: { fecha?: string; profesor_id?: number }) {
    let httpParams = new HttpParams();
    if (params?.fecha) httpParams = httpParams.set('fecha', params.fecha);
    if (params?.profesor_id) httpParams = httpParams.set('profesor_id', String(params.profesor_id));
    return this.http.get<Ausencia[]>(`${this.url}/`, { params: httpParams });
  }

  crear(data: { fecha: string; horas: number[]; descripcion?: string; profesor_id?: number }) {
    return this.http.post<{
      creadas: Ausencia[];
      ignoradas: number[];
      ya_existentes: Ausencia[];
      mensaje: string;
    }>(`${this.url}/crear/`, data);
  }

  eliminar(id: number) {
    return this.http.delete(`${this.url}/${id}/`);
  }

  justificar(id: number, justificada: boolean) {
    return this.http.patch<Ausencia>(`${this.url}/${id}/justificar/`, { justificada });
  }

  porFecha(fecha: string) {
    return this.http.get<Ausencia[]>(`${this.url}/fecha/${fecha}/`);
  }
}
