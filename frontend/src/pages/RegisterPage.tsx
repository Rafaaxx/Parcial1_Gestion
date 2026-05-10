/**
 * RegisterPage — User registration form
 */

import React, { useState } from 'react'
import { Link, useNavigate, Navigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { useAuthStore } from '@/features/auth/store'
import { apiClient } from '@/shared/http/client'
import { Input } from '@/shared/ui/Input'
import { Button } from '@/shared/ui/Button'

interface RegisterPayload {
  nombre: string
  apellido: string
  email: string
  password: string
}

interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

interface MeResponse {
  id: number
  nombre: string
  apellido: string
  email: string
  roles: string[]
  activo: boolean
}

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const { isAuthenticated, rehydrated, setTokens, setUser } = useAuthStore()

  const [nombre, setNombre] = useState('')
  const [apellido, setApellido] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  // If already authenticated, redirect (use Navigate component, not navigate() side-effect)
  if (rehydrated && isAuthenticated) {
    return <Navigate to="/" replace />
  }

  const registerMutation = useMutation({
    mutationFn: async (data: RegisterPayload) => {
      const tokenResp = await apiClient.post<TokenResponse>('/auth/register', data)
      const { access_token, refresh_token } = tokenResp.data

      // Set tokens immediately so /auth/me can use them
      setTokens(access_token, refresh_token)

      // Fetch user data from /auth/me
      const meResp = await apiClient.get<MeResponse>('/auth/me')
      const userData = meResp.data

      setUser({
        id: String(userData.id),
        email: userData.email,
        name: `${userData.nombre} ${userData.apellido}`,
        roles: userData.roles as Array<'ADMIN' | 'STOCK' | 'PEDIDOS' | 'CLIENT'>,
      })

      return tokenResp.data
    },
    onSuccess: () => {
      navigate('/', { replace: true })
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { detail?: string | Record<string, string> } } }
      const detail = axiosError?.response?.data?.detail

      if (typeof detail === 'object' && detail !== null) {
        setFieldErrors(detail as Record<string, string>)
        setError('Por favor, corregí los errores del formulario.')
      } else if (typeof detail === 'string') {
        setError(detail)
      } else {
        setError('Ocurrió un error al registrarse. Intentá de nuevo.')
      }
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setFieldErrors({})

    // Client-side validation
    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden.')
      return
    }

    if (nombre.trim().length < 2) {
      setFieldErrors({ nombre: 'El nombre debe tener al menos 2 caracteres.' })
      return
    }

    registerMutation.mutate({
      nombre: nombre.trim(),
      apellido: apellido.trim(),
      email: email.trim(),
      password,
    })
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="card-base p-8">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50 mb-2">
              Crear Cuenta
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Completá tus datos para registrarte
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-300">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="nombre" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Nombre
                </label>
                <Input
                  id="nombre"
                  type="text"
                  value={nombre}
                  onChange={(e) => setNombre(e.target.value)}
                  placeholder="Juan"
                  required
                  autoComplete="given-name"
                />
                {fieldErrors.nombre && (
                  <p className="mt-1 text-xs text-red-500">{fieldErrors.nombre}</p>
                )}
              </div>
              <div>
                <label htmlFor="apellido" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Apellido
                </label>
                <Input
                  id="apellido"
                  type="text"
                  value={apellido}
                  onChange={(e) => setApellido(e.target.value)}
                  placeholder="Pérez"
                  required
                  autoComplete="family-name"
                />
                {fieldErrors.apellido && (
                  <p className="mt-1 text-xs text-red-500">{fieldErrors.apellido}</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu@email.com"
                required
                autoComplete="email"
              />
              {fieldErrors.email && (
                <p className="mt-1 text-xs text-red-500">{fieldErrors.email}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Contraseña
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                autoComplete="new-password"
                minLength={6}
              />
              {fieldErrors.password && (
                <p className="mt-1 text-xs text-red-500">{fieldErrors.password}</p>
              )}
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Confirmar Contraseña
              </label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                required
                autoComplete="new-password"
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={registerMutation.isPending}
            >
              {registerMutation.isPending ? 'Registrando...' : 'Crear Cuenta'}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
            ¿Ya tenés cuenta?{' '}
            <Link
              to="/auth/login"
              className="text-primary-600 dark:text-primary-400 hover:underline font-medium"
            >
              Iniciar Sesión
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
