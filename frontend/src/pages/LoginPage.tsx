/**
 * LoginPage — Authentication form
 */

import React, { useState } from 'react'
import { Link, useNavigate, useSearchParams, Navigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { useAuthStore } from '@/features/auth/store'
import { apiClient } from '@/shared/http/client'
import { Input } from '@/shared/ui/Input'
import { Button } from '@/shared/ui/Button'

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

export const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const redirect = searchParams.get('redirect') || '/'
  const { isAuthenticated, rehydrated, setTokens, setUser } = useAuthStore()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  // If already authenticated, redirect (use Navigate component, not navigate() side-effect)
  if (rehydrated && isAuthenticated) {
    return <Navigate to="/" replace />
  }

  const loginMutation = useMutation({
    mutationFn: async (data: { email: string; password: string }) => {
      const tokenResp = await apiClient.post<TokenResponse>('/auth/login', data)
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
      navigate(redirect, { replace: true })
    },
    onError: (error: unknown) => {
      const axiosError = error as { response?: { data?: { detail?: string } } }
      setError(axiosError?.response?.data?.detail || 'Credenciales inválidas')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    loginMutation.mutate({ email, password })
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="card-base p-8">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50 mb-2">
              Iniciar Sesión
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Ingresá tus credenciales para continuar
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-300">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
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
                autoComplete="current-password"
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={loginMutation.isPending}
            >
              {loginMutation.isPending ? 'Ingresando...' : 'Iniciar Sesión'}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
            ¿No tenés cuenta?{' '}
            <Link
              to="/auth/register"
              className="text-primary-600 dark:text-primary-400 hover:underline font-medium"
            >
              Registrarse
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
