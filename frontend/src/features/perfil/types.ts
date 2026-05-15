/**
 * Types for Perfil (Profile) module
 */

// ── Profile Data ───────────────────────────────────────────────────────────

export interface PerfilData {
  id: number
  nombre: string
  apellido: string
  email: string
  telefono: string | null
  roles: string[]
  fecha_registro: string
}

export interface PerfilUpdate {
  nombre?: string
  apellido?: string
  telefono?: string
}

export interface PasswordChange {
  password_actual: string
  password_nueva: string
}

export interface PasswordChangeResponse {
  message: string
  requires_relogin: boolean
}
