/**
 * useCartDrawer — custom hook to manage cart drawer open/close state
 */

import { useState, useCallback, useMemo } from 'react'

interface UseCartDrawerReturn {
  isOpen: boolean
  openCart: () => void
  closeCart: () => void
  toggleCart: () => void
}

export function useCartDrawer(): UseCartDrawerReturn {
  const [isOpen, setIsOpen] = useState(false)

  const openCart = useCallback(() => setIsOpen(true), [])
  const closeCart = useCallback(() => setIsOpen(false), [])
  const toggleCart = useCallback(() => setIsOpen((prev) => !prev), [])

  return useMemo(
    () => ({ isOpen, openCart, closeCart, toggleCart }),
    [isOpen, openCart, closeCart, toggleCart]
  )
}

export default useCartDrawer
