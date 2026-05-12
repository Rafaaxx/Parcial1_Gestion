/**
 * ToastNotifier — simple state-based toast notification system
 *
 * No external library. Renders a fixed-position toast container at top-right.
 * Usage: wrap your app or use the hook to show toasts from any component.
 */

import React, { useState, useCallback, useRef, useEffect } from 'react'

export interface ToastMessage {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
}

interface ToastNotifierContextValue {
  showToast: (type: ToastMessage['type'], message: string) => void
}

const ToastNotifierContext = React.createContext<ToastNotifierContextValue | null>(null)

let toastIdCounter = 0

export function useToast(): ToastNotifierContextValue {
  const ctx = React.useContext(ToastNotifierContext)
  if (!ctx) {
    // Fallback: return a no-op if used outside provider (avoids crashes during development)
    return { showToast: () => {} }
  }
  return ctx
}

export const ToastNotifierProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastMessage[]>([])
  const timersRef = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map())

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
    const timer = timersRef.current.get(id)
    if (timer) {
      clearTimeout(timer)
      timersRef.current.delete(id)
    }
  }, [])

  const showToast = useCallback(
    (type: ToastMessage['type'], message: string) => {
      const id = `toast-${++toastIdCounter}`
      const newToast: ToastMessage = { id, type, message }
      setToasts((prev) => [...prev, newToast])

      // Auto-dismiss after 3 seconds
      const timer = setTimeout(() => removeToast(id), 3000)
      timersRef.current.set(id, timer)
    },
    [removeToast]
  )

  // Cleanup all timers on unmount
  useEffect(() => {
    return () => {
      timersRef.current.forEach((timer) => clearTimeout(timer))
      timersRef.current.clear()
    }
  }, [])

  const typeStyles: Record<ToastMessage['type'], string> = {
    success: 'bg-green-600 text-white',
    error: 'bg-red-600 text-white',
    warning: 'bg-yellow-500 text-white',
    info: 'bg-blue-600 text-white',
  }

  const icons: Record<ToastMessage['type'], string> = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ⓘ',
  }

  return (
    <ToastNotifierContext.Provider value={{ showToast }}>
      {children}

      {/* Toast container */}
      <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`${typeStyles[toast.type]} rounded-lg shadow-lg px-4 py-3 flex items-center gap-3 min-w-[280px] max-w-[400px] pointer-events-auto animate-slide-in-right`}
            role="alert"
          >
            <span className="font-bold text-lg flex-shrink-0">{icons[toast.type]}</span>
            <span className="flex-1 text-sm font-medium">{toast.message}</span>
            <button
              onClick={() => removeToast(toast.id)}
              className="flex-shrink-0 hover:opacity-80"
              aria-label="Cerrar"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        ))}
      </div>
    </ToastNotifierContext.Provider>
  )
}

export default ToastNotifierProvider
