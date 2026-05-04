export interface Usuario {
  id: number;
  email: string;
  role: 'PROFESORADO' | 'EQUIPO_DIRECTIVO';
  must_change_password: boolean;
  profesor?: Profesor;
}

export interface Profesor {
  id: number;
  nombre: string;
  email_institucional: string;
  tiene_cuenta: boolean;
}

export interface HorarioEntry {
  id: number;
  asignatura: string;
  curso: string;
  aula: string;
  profesor_id: number;
  profesor_nombre: string;
  dia: string;
  dia_display: string;
  hora: number;
  es_guardia: boolean;
  es_recreo: boolean;
}

export interface Ausencia {
  id: number;
  fecha: string;
  descripcion: string;
  justificada: boolean;
  horario_entry: number;
  profesor_nombre: string;
  asignatura: string;
  aula: string;
  hora: number;
  dia: string;
  creada_en: string;
}

export interface ParteAusencias {
  id: number;
  fecha: string;
  tipo: 'A' | 'B';
  tipo_display: string;
  generado_en: string;
  pdf_url: string | null;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  usuario: Usuario;
}
