/**
 * ProfilePage — User profile management
 *
 * Three sections:
 * - Mis Datos: View/edit personal info (nombre, apellido, telefono)
 * - Cambiar Contraseña: Change password with current password validation
 * - Mis Direcciones: List delivery addresses
 */

import React, { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/shared/hooks/useAuth'
import { usePerfil, useUpdatePerfil, useChangePassword } from '@/features/perfil/hooks'
import type { PerfilUpdate, PasswordChange } from '@/features/perfil/types'
import { DireccionModal } from '@/features/direcciones/components/DireccionModal'

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

interface DireccionFormData {
  alias: string
  linea1: string
}

// Helper to get auth headers
function getAuthHeaders(): Record<string, string> {
  const stored = localStorage.getItem('food-store-auth')
  let headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (stored) {
    const parsed = JSON.parse(stored)
    const token = parsed.state?.token
    if (token) {
      headers = { ...headers, Authorization: `Bearer ${token}` }
    }
  }
  return headers
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function MisDireccionesSection() {
  const [direcciones, setDirecciones] = useState<DireccionItem[] | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isError, setIsError] = useState(false)
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingDireccion, setEditingDireccion] = useState<DireccionItem | null>(null)
  const [formData, setFormData] = useState<DireccionFormData>({ alias: '', linea1: '' })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  // Delete confirmation state
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; direccion: DireccionItem | null }>({
    isOpen: false,
    direccion: null,
  })

  const fetchDirecciones = useCallback(async () => {
    setIsLoading(true)
    setIsError(false)
    try {
      const response = await fetch(`${API_BASE}/api/v1/direcciones?skip=0&limit=100`, {
        headers: getAuthHeaders(),
      })
      if (!response.ok) throw new Error(`Error ${response.status}`)
      const data: DireccionListResponse = await response.json()
      setDirecciones(data.items ?? [])
    } catch {
      setIsError(true)
    } finally {
      setIsLoading(false)
    }
  }, [])

  React.useEffect(() => {
    fetchDirecciones()
  }, [fetchDirecciones])

  // Open create modal
  const openCreateModal = () => {
    setEditingDireccion(null)
    setFormData({ alias: '', linea1: '' })
    setSubmitError(null)
    setIsModalOpen(true)
  }

  // Open edit modal
  const openEditModal = (dir: DireccionItem) => {
    setEditingDireccion(dir)
    setFormData({
      alias: dir.alias ?? '',
      linea1: dir.linea1,
    })
    setSubmitError(null)
    setIsModalOpen(true)
  }

  // Close modal
  const closeModal = () => {
    setIsModalOpen(false)
    setEditingDireccion(null)
    setFormData({ alias: '', linea1: '' })
    setSubmitError(null)
  }

  // Handle submit (create or update)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setSubmitError(null)

    try {
      const url = editingDireccion
        ? `${API_BASE}/api/v1/direcciones/${editingDireccion.id}`
        : `${API_BASE}/api/v1/direcciones`
      
      const method = editingDireccion ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: getAuthHeaders(),
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Error ${response.status}`)
      }

      await fetchDirecciones()
      closeModal()
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Error al guardar')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Set as principal
  const handleSetPrincipal = async (dir: DireccionItem) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/direcciones/${dir.id}/predeterminada`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
      })
      if (!response.ok) throw new Error(`Error ${response.status}`)
      await fetchDirecciones()
    } catch (err) {
      console.error('Error setting principal:', err)
    }
  }

  // Open delete confirmation
  const openDeleteConfirm = (dir: DireccionItem) => {
    setDeleteConfirm({ isOpen: true, direccion: dir })
  }

  // Confirm delete
  const handleDelete = async () => {
    if (!deleteConfirm.direccion) return
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/direcciones/${deleteConfirm.direccion.id}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      })
      if (!response.ok) throw new Error(`Error ${response.status}`)
      await fetchDirecciones()
    } catch (err) {
      console.error('Error deleting:', err)
    } finally {
      setDeleteConfirm({ isOpen: false, direccion: null })
    }
  }

  const closeDeleteConfirm = () => {
    setDeleteConfirm({ isOpen: false, direccion: null })
  }

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
    <>
      <div className="card-base p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
            Mis Direcciones
          </h2>
          <button
            onClick={openCreateModal}
            className="px-3 py-1.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Agregar
          </button>
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
                  <div className="flex items-center gap-1 ml-2">
                    {dir.es_principal ? (
                      <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300">
                        Principal
                      </span>
                    ) : (
                      <button
                        onClick={() => handleSetPrincipal(dir)}
                        className="p-1.5 text-xs text-gray-500 hover:text-primary-600 dark:text-gray-400 dark:hover:text-primary-400"
                        title="Hacer principal"
                      >
                        Marcar principal
                      </button>
                    )}
                  </div>
                </div>
                
                {/* Action buttons */}
                <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                  <button
                    onClick={() => openEditModal(dir)}
                    className="text-xs text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                  >
                    Editar
                  </button>
                  <span className="text-gray-300 dark:text-gray-600">|</span>
                  <button
                    onClick={() => openDeleteConfirm(dir)}
                    className="text-xs text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      <DireccionModal
        isOpen={isModalOpen}
        onClose={closeModal}
        onSubmit={handleSubmit}
        formData={formData}
        setFormData={setFormData}
        isEditing={!!editingDireccion}
        isSubmitting={isSubmitting}
        error={submitError}
      />

      {/* Delete Confirmation Dialog */}
      {deleteConfirm.isOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-2">
              Eliminar Dirección
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              ¿Estás seguro de eliminar esta dirección? Esta acción no se puede deshacer.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={closeDeleteConfirm}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Cancelar
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
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
