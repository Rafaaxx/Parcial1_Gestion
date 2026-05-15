/**
 * ProfilePage — User profile management
 *
 * Three sections:
 * - Mis Datos: View/edit personal info (nombre, apellido, telefono)
 * - Cambiar Contraseña: Change password with current password validation
 * - Mis Direcciones: List delivery addresses
 */

import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/shared/hooks/useAuth'
import { usePerfil, useUpdatePerfil, useChangePassword } from '@/features/perfil/hooks'
import type { PerfilUpdate, PasswordChange } from '@/features/perfil/types'

// ═══════════════════════════════════════════════════════════════════════════
// Data Section
// ═══════════════════════════════════════════════════════════════════════════

function MisDatosSection() {
  const { data: perfil, isLoading, isError } = usePerfil()
  const updateMutation = useUpdatePerfil()
  const { user: authUser } = useAuth()

  const [isEditing, setIsEditing] = useState(false)
  const [form, setForm] = useState<PerfilUpdate>({})

  // Initialize form when entering edit mode
  const startEditing = () => {
    if (perfil) {
      setForm({
        nombre: perfil.nombre,
        apellido: perfil.apellido,
        telefono: perfil.telefono ?? '',
      })
      setIsEditing(true)
    }
  }

  const cancelEditing = () => {
    setIsEditing(false)
    setForm({})
  }

  const handleSave = async () => {
    // Validate at least one field changed
    const hasChanges =
      form.nombre !== perfil?.nombre ||
      form.apellido !== perfil?.apellido ||
      form.telefono !== (perfil?.telefono ?? '')

    if (!hasChanges) {
      setIsEditing(false)
      return
    }

    try {
      await updateMutation.mutateAsync(form)
      setIsEditing(false)
      setForm({})
    } catch {
      // error handled by mutation
    }
  }

  if (isLoading) {
    return (
      <div className="card-base p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
        </div>
      </div>
    )
  }

  if (isError || !perfil) {
    return (
      <div className="card-base p-8 text-center">
        <p className="text-red-600 dark:text-red-400">
          Error al cargar los datos del perfil.
        </p>
      </div>
    )
  }

  const fieldClass =
    'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100'
  const labelClass = 'block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1'
  const valueClass = 'text-gray-900 dark:text-gray-100'

  // ── View Mode ──────────────────────────────────────────────────────────
  if (!isEditing) {
    return (
      <div className="card-base p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
            Mis Datos
          </h2>
          <button
            onClick={startEditing}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
          >
            Editar
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Nombre</p>
            <p className={valueClass}>{perfil.nombre}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Apellido</p>
            <p className={valueClass}>{perfil.apellido}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Email</p>
            <p className={valueClass}>{perfil.email}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Teléfono</p>
            <p className={valueClass}>{perfil.telefono || '—'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Fecha de registro
            </p>
            <p className={valueClass}>
              {new Date(perfil.fecha_registro).toLocaleDateString('es-AR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Rol</p>
            <p className={valueClass}>{perfil.roles.join(', ')}</p>
          </div>
        </div>
      </div>
    )
  }

  // ── Edit Mode ──────────────────────────────────────────────────────────
  return (
    <div className="card-base p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
          Editar Mis Datos
        </h2>
        <span className="text-xs text-gray-400">Email no modificable</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Nombre</label>
          <input
            type="text"
            value={form.nombre ?? ''}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })}
            className={fieldClass}
            minLength={2}
            maxLength={100}
          />
        </div>
        <div>
          <label className={labelClass}>Apellido</label>
          <input
            type="text"
            value={form.apellido ?? ''}
            onChange={(e) => setForm({ ...form, apellido: e.target.value })}
            className={fieldClass}
            minLength={2}
            maxLength={100}
          />
        </div>
        <div>
          <label className={labelClass}>Email</label>
          <input
            type="email"
            value={perfil.email}
            disabled
            className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-500 dark:text-gray-400 cursor-not-allowed"
          />
        </div>
        <div>
          <label className={labelClass}>Teléfono</label>
          <input
            type="text"
            value={form.telefono ?? ''}
            onChange={(e) => setForm({ ...form, telefono: e.target.value })}
            className={fieldClass}
            maxLength={20}
            placeholder="+541112345678"
          />
        </div>
      </div>

      {updateMutation.isError && (
        <p className="mt-4 text-sm text-red-600 dark:text-red-400">
          {(updateMutation.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
            'Error al guardar los cambios'}
        </p>
      )}

      <div className="flex gap-3 mt-6">
        <button
          onClick={handleSave}
          disabled={updateMutation.isPending}
          className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors disabled:opacity-50"
        >
          {updateMutation.isPending ? 'Guardando...' : 'Guardar cambios'}
        </button>
        <button
          onClick={cancelEditing}
          disabled={updateMutation.isPending}
          className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          Cancelar
        </button>
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
// Password Section
// ═══════════════════════════════════════════════════════════════════════════

function CambiarPasswordSection() {
  const navigate = useNavigate()
  const changePasswordMutation = useChangePassword()
  const { logout } = useAuth()

  const [form, setForm] = useState<PasswordChange>({
    password_actual: '',
    password_nueva: '',
  })
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  // Validation
  const isNewPasswordValid = form.password_nueva.length >= 8

  const handleChange = (field: keyof PasswordChange, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSuccessMsg(null)

    if (!form.password_actual || !form.password_nueva) return
    if (!isNewPasswordValid) return

    try {
      const result = await changePasswordMutation.mutateAsync(form)
      setSuccessMsg(result.message)

      // Clear form
      setForm({ password_actual: '', password_nueva: '' })

      // Force re-login after a short delay (all tokens revoked per US-063)
      setTimeout(() => {
        logout()
        navigate('/login')
      }, 3000)
    } catch {
      // error handled by mutation
    }
  }

  const inputClass =
    'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100'
  const labelClass = 'block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1'

  return (
    <div className="card-base p-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-6">
        Cambiar Contraseña
      </h2>

      {successMsg ? (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <p className="text-sm text-green-700 dark:text-green-300">{successMsg}</p>
          <p className="text-sm text-green-600 dark:text-green-400 mt-1">
            Serás redirigido al inicio de sesión en 3 segundos...
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
          <div>
            <label className={labelClass} htmlFor="password-actual">
              Contraseña actual
            </label>
            <input
              id="password-actual"
              type="password"
              value={form.password_actual}
              onChange={(e) => handleChange('password_actual', e.target.value)}
              className={inputClass}
              required
              placeholder="Ingresá tu contraseña actual"
            />
          </div>

          <div>
            <label className={labelClass} htmlFor="password-nueva">
              Nueva contraseña
            </label>
            <input
              id="password-nueva"
              type="password"
              value={form.password_nueva}
              onChange={(e) => handleChange('password_nueva', e.target.value)}
              className={inputClass}
              required
              minLength={8}
              placeholder={'Mínimo 8 caracteres'}
            />
            {form.password_nueva.length > 0 && !isNewPasswordValid && (
              <p className="mt-1 text-xs text-red-500">
                La contraseña debe tener al menos 8 caracteres
              </p>
            )}
          </div>

          {changePasswordMutation.isError && (
            <p className="text-sm text-red-600 dark:text-red-400">
              {(changePasswordMutation.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
                'Error al cambiar la contraseña'}
            </p>
          )}

          <button
            type="submit"
            disabled={
              changePasswordMutation.isPending ||
              !form.password_actual ||
              !form.password_nueva ||
              !isNewPasswordValid
            }
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors disabled:opacity-50"
          >
            {changePasswordMutation.isPending
              ? 'Cambiando...'
              : 'Cambiar contraseña'}
          </button>
        </form>
      )}
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
// Direcciones Section
// ═══════════════════════════════════════════════════════════════════════════

interface DireccionItem {
  id: number
  alias: string | null
  linea1: string
  es_principal: boolean
  created_at: string
  updated_at: string
  deleted_at: string | null
}

interface DireccionListResponse {
  items: DireccionItem[]
  total: number
  skip: number
  limit: number
}

function MisDireccionesSection() {
  const [direcciones, setDirecciones] = useState<DireccionItem[] | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isError, setIsError] = useState(false)

  // Fetch addresses on mount
  React.useEffect(() => {
    const fetchDirecciones = async () => {
      setIsLoading(true)
      setIsError(false)

      try {
        const stored = localStorage.getItem('food-store-auth')
        let headers: Record<string, string> = {}
        if (stored) {
          const parsed = JSON.parse(stored)
          const token = parsed.state?.token
          if (token) {
            headers = { Authorization: `Bearer ${token}` }
          }
        }

        const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const response = await fetch(
          `${API_BASE}/api/v1/direcciones?skip=0&limit=100`,
          { headers }
        )

        if (!response.ok) {
          throw new Error(`Error ${response.status}`)
        }

        const data: DireccionListResponse = await response.json()
        setDirecciones(data.items ?? [])
      } catch {
        setIsError(true)
      } finally {
        setIsLoading(false)
      }
    }

    fetchDirecciones()
  }, [])

  if (isLoading) {
    return (
      <div className="card-base p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
          Mis Direcciones
        </h2>
        <div className="animate-pulse space-y-3">
          <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded-lg" />
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="card-base p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
          Mis Direcciones
        </h2>
        <p className="text-sm text-red-600 dark:text-red-400">
          Error al cargar las direcciones.
        </p>
      </div>
    )
  }

  const hasDirecciones = direcciones && direcciones.length > 0

  return (
    <div className="card-base p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
          Mis Direcciones
        </h2>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {hasDirecciones ? `${direcciones!.length} direccion${direcciones!.length === 1 ? '' : 'es'}` : ''}
        </span>
      </div>

      {!hasDirecciones ? (
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
          No tenés direcciones guardadas.
        </p>
      ) : (
        <div className="space-y-3">
          {direcciones!.map((dir) => (
            <div
              key={dir.id}
              className={`p-4 border rounded-lg ${
                dir.es_principal
                  ? 'border-primary-300 dark:border-primary-600 bg-primary-50 dark:bg-primary-900/10'
                  : 'border-gray-200 dark:border-gray-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {dir.alias && (
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {dir.alias}
                    </p>
                  )}
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {dir.linea1}
                  </p>
                </div>
                {dir.es_principal && (
                  <span className="ml-2 px-2 py-0.5 text-xs font-medium rounded-full bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 shrink-0">
                    Principal
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
// Page
// ═══════════════════════════════════════════════════════════════════════════

export const ProfilePage: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
        Mi Perfil
      </h1>

      <MisDatosSection />
      <CambiarPasswordSection />
      <MisDireccionesSection />
    </div>
  )
}

export default ProfilePage
