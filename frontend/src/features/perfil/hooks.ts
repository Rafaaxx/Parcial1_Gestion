/**
 * Custom hooks for Perfil module using TanStack Query
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getPerfil, updatePerfil, changePassword } from './api'
import type { PerfilUpdate, PasswordChange } from './types'

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export const perfilKeys = {
  all: ['perfil'] as const,
  detail: () => [...perfilKeys.all, 'detail'] as const,
}

// ═══════════════════════════════════════════════════════════════════════════
// Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get the authenticated user's profile
 */
export function usePerfil() {
  return useQuery({
    queryKey: perfilKeys.detail(),
    queryFn: getPerfil,
  })
}

/**
 * Update profile fields (nombre, apellido, telefono)
 * Invalidates the profile query on success
 */
export function useUpdatePerfil() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: PerfilUpdate) => updatePerfil(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: perfilKeys.all })
    },
  })
}

/**
 * Change password
 * Does NOT invalidate any queries — the user will be redirected to login
 * after password change (all tokens revoked)
 */
export function useChangePassword() {
  return useMutation({
    mutationFn: (data: PasswordChange) => changePassword(data),
  })
}
