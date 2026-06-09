import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { HorarioEntry } from '../models';

interface PaginatedResponse<T> { count: number; results: T[]; }

export interface ImportScheduleResult {
  total_lineas: number;
  filas_importadas: number;
  filas_duplicadas: number;
  profesores_creados: number;
  filas_con_error: number;
  errores: string[];
  importados: number;
  profesores: number;
}

export interface FiltrosHorario {
  profesor_id?: number;
  profesor_nombre?: string;
  dia?: string;
  grupo?: string;
  asignatura?: string;
  aula?: string;
}

@Injectable({ providedIn: 'root' })
export class ScheduleService {
  private url = `${environment.apiUrl}/schedules`;

  constructor(private http: HttpClient) {}

  miHorario() {
    return this.http.get<HorarioEntry[]>(`${this.url}/mi-horario/`);
  }

  buscar(filtros: FiltrosHorario) {
    let params = new HttpParams().set('page_size', '200');
    if (filtros.profesor_id) params = params.set('profesor_id', String(filtros.profesor_id));
    if (filtros.profesor_nombre) params = params.set('profesor_nombre', filtros.profesor_nombre);
    if (filtros.dia)             params = params.set('dia', filtros.dia);
    if (filtros.grupo)           params = params.set('grupo', filtros.grupo);
    if (filtros.asignatura)      params = params.set('asignatura', filtros.asignatura);
    if (filtros.aula)            params = params.set('aula', filtros.aula);
    return this.http
      .get<PaginatedResponse<HorarioEntry>>(`${this.url}/`, { params })
      .pipe(map(r => r.results));
  }

  importar(file: File) {
    const form = new FormData();
    form.append('fichero', file);
    return this.http.post<ImportScheduleResult>(
      `${this.url}/importar/`,
      form,
    );
  }
}
