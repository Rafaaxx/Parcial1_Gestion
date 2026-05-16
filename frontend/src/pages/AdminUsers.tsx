/**
 * AdminUsers — User management with CRUD operations
 */

import React, { useState } from 'react'
import { useUsuarios, useUpdateUsuario, useUpdateUsuarioEstado } from '@/features/admin'
import type { UsuarioAdmin } from '@/features/admin'

const ROLES = ['ADMIN', 'STOCK', 'PEDIDOS', 'CLIENT']

export const AdminUsers: React.FC = () => {
  const [search, setSearch] = useState('')
  const [rolFilter, setRolFilter] = useState<string>('')
  const [activoFilter, setActivoFilter] = useState<string>('')
  const [editingUser, setEditingUser] = useState<UsuarioAdmin | null>(null)
  const [editForm, setEditForm] = useState({ nombre: '', email: '', roles_codes: [] as string[] })

  const { data, isLoading, refetch } = useUsuarios(0, 50, search, rolFilter || undefined, activoFilter === '' ? undefined : activoFilter === 'true')
  const updateUsuario = useUpdateUsuario()
  const updateEstado = useUpdateUsuarioEstado()

  const handleEdit = (user: UsuarioAdmin) => {
    setEditingUser(user)
    setEditForm({
      nombre: user.nombre,
      email: user.email,
      roles_codes: [...user.roles],
    })
  }

  const handleSave = async () => {
    if (!editingUser) return

    await updateUsuario.mutateAsync({
      usuarioId: editingUser.id,
      data: {
        nombre: editForm.nombre,
        email: editForm.email,
        roles_codes: editForm.roles_codes,
      },
    })
    setEditingUser(null)
    refetch()
  }

  const handleToggleActivo = async (user: UsuarioAdmin) => {
    await updateEstado.mutateAsync({
      usuarioId: user.id,
      data: { activo: !user.activo },
    })
    refetch()
  }

  const handleRoleToggle = (rol: string) => {
    setEditForm((prev) => ({
      ...prev,
      roles_codes: prev.roles_codes.includes(rol)
        ? prev.roles_codes.filter((r) => r !== rol)
        : [...prev.roles_codes, rol],
    }))
  }

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
        Gestión de Usuarios
      </h1>

      {/* Filtros */}
      <div className="flex flex-wrap gap-4">
        <input
          type="text"
          placeholder="Buscar por nombre o email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 flex-1 min-w-[200px]"
        />
        <select
          value={rolFilter}
          onChange={(e) => setRolFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        >
          <option value="">Todos los roles</option>
          {ROLES.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
        <select
          value={activoFilter}
          onChange={(e) => setActivoFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        >
          <option value="">Todos los estados</option>
          <option value="true">Activos</option>
          <option value="false">Inactivos</option>
        </select>
      </div>

      {/* Tabla */}
      <div className="card-base overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">ID</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Nombre</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Email</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Roles</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Estado</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Último Login</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {data?.items.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">{user.id}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">{user.nombre}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">{user.email}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {user.roles.map((rol) => (
                          <span
                            key={rol}
                            className={`px-2 py-1 text-xs font-medium rounded ${
                              rol === 'ADMIN'
                                ? 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200'
                                : rol === 'STOCK'
                                ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                                : rol === 'PEDIDOS'
                                ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
                                : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                            }`}
                          >
                            {rol}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${
                          user.activo
                            ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                            : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                        }`}
                      >
                        {user.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                      {user.ultimo_login ? new Date(user.ultimo_login).toLocaleDateString('es-AR') : '-'}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleEdit(user)}
                          className="px-3 py-1 text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleToggleActivo(user)}
                          className={`px-3 py-1 text-xs font-medium ${
                            user.activo
                              ? 'text-red-600 dark:text-red-400 hover:underline'
                              : 'text-green-600 dark:text-green-400 hover:underline'
                          }`}
                        >
                          {user.activo ? 'Desactivar' : 'Activar'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {data && (
          <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-500 dark:text-gray-400">
            Total: {data.total} usuarios
          </div>
        )}
      </div>

      {/* Modal de edición */}
      {editingUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-50 mb-4">
              Editar Usuario #{editingUser.id}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Nombre
                </label>
                <input
                  type="text"
                  value={editForm.nombre}
                  onChange={(e) => setEditForm({ ...editForm, nombre: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={editForm.email}
                  onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Roles
                </label>
                <div className="flex flex-wrap gap-2">
                  {ROLES.map((rol) => (
                    <label
                      key={rol}
                      className="flex items-center gap-2 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      <input
                        type="checkbox"
                        checked={editForm.roles_codes.includes(rol)}
                        onChange={() => handleRoleToggle(rol)}
                        className="rounded"
                      />
                      <span className="text-sm text-gray-900 dark:text-gray-100">{rol}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setEditingUser(null)}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                Cancelar
              </button>
              <button
                onClick={handleSave}
                disabled={updateUsuario.isPending}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {updateUsuario.isPending ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminUsers
