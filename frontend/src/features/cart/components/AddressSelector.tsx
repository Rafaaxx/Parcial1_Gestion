/**
 * AddressSelector — Component to select delivery address in the cart/checkout
 *
 * Shows a list of user's addresses and allows selection.
 * If no addresses exist, shows a link to create one in the profile.
 */

import React, { useEffect, useState } from 'react'
import { usePaymentStore } from '../stores/paymentStore'

// Address type matching the backend DireccionRead schema
interface Direccion {
  id: number
  alias: string | null
  linea1: string
  es_principal: boolean
}

interface AddressSelectorProps {
  /** Called when address selection changes */
  onAddressChange?: (direccionId: number | null) => void
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const AddressSelector: React.FC<AddressSelectorProps> = ({ onAddressChange }) => {
  console.log('🔵 AddressSelector MOUNTED - this should show in console!')
  const [direcciones, setDirecciones] = useState<Direccion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Get current selected address from store
  const selectedDireccionId = usePaymentStore((s) => s.direccionId)
  const setDireccion = usePaymentStore((s) => s.setDireccion)

  console.log('AddressSelector render:', { loading, direcciones, error, selectedDireccionId })

  // Fetch addresses on mount
  useEffect(() => {
    const fetchDirecciones = async () => {
      try {
        const token = localStorage.getItem('access_token')
        console.log('AddressSelector: token exists:', !!token)
        const headers: Record<string, string> = { 'Content-Type': 'application/json' }
        if (token) headers['Authorization'] = `Bearer ${token}`

        console.log('AddressSelector: fetching direcciones from API...')
        const response = await fetch(`${API_BASE}/api/v1/direcciones?skip=0&limit=100`, {
          headers,
        })
        console.log('AddressSelector: response status:', response.status)

        if (!response.ok) {
          // If 401/403, user not logged in - not an error, just no addresses
          if (response.status === 401 || response.status === 403) {
            setDirecciones([])
            setLoading(false)
            return
          }
          throw new Error('Error al cargar direcciones')
        }

        const data = await response.json()
        setDirecciones(data.items || [])
      } catch (err) {
        console.error('Error fetching direcciones:', err)
        setError('No se pudieron cargar las direcciones')
        setDirecciones([])
      } finally {
        setLoading(false)
      }
    }

    fetchDirecciones()
  }, [])

  // Auto-select default address (principal) if none selected
  useEffect(() => {
    if (!selectedDireccionId && direcciones.length > 0) {
      const principal = direcciones.find((d) => d.es_principal)
      if (principal) {
        setDireccion(principal.id)
        onAddressChange?.(principal.id)
      }
    }
  }, [direcciones, selectedDireccionId, setDireccion, onAddressChange])

  const handleSelect = (direccionId: number) => {
    setDireccion(direccionId)
    onAddressChange?.(direccionId)
  }

  // Handle "no delivery" (pickup at location)
  const handlePickup = () => {
    setDireccion(null)
    onAddressChange?.(null)
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-2">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
        <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-sm text-red-600 dark:text-red-400 p-2">
        {error}
      </div>
    )
  }

  // No addresses - show option for pickup or link to create
  if (direcciones.length === 0) {
    return (
      <div className="space-y-3 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
        <div className="flex items-center gap-2">
          <input
            type="radio"
            id="pickup"
            name="delivery"
            checked={selectedDireccionId === null}
            onChange={handlePickup}
            className="w-4 h-4 text-primary-600 border-gray-300 focus:ring-primary-500"
          />
          <label htmlFor="pickup" className="text-sm text-gray-700 dark:text-gray-300 font-medium">
            Retirar en local (sin costo de envío)
          </label>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          ¿Querés agregar una dirección?{' '}
          <a href="/perfil" className="text-primary-600 hover:text-primary-700 dark:text-primary-400">
            Ir a Mi Perfil
          </a>
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
        Dirección de entrega
      </h4>

      {/* Pickup option */}
      <div className="flex items-center gap-2">
        <input
          type="radio"
          id="pickup"
          name="delivery"
          checked={selectedDireccionId === null}
          onChange={handlePickup}
          className="w-4 h-4 text-primary-600 border-gray-300 focus:ring-primary-500"
        />
        <label htmlFor="pickup" className="text-sm text-gray-700 dark:text-gray-300">
          Retirar en local (sin costo de envío)
        </label>
      </div>

      {/* Address options */}
      {direcciones.map((direccion) => (
        <div key={direccion.id} className="flex items-start gap-2">
          <input
            type="radio"
            id={`direccion-${direccion.id}`}
            name="delivery-address"
            checked={selectedDireccionId === direccion.id}
            onChange={() => handleSelect(direccion.id)}
            className="mt-1 w-4 h-4 text-primary-600 border-gray-300 focus:ring-primary-500"
          />
          <label
            htmlFor={`direccion-${direccion.id}`}
            className="text-sm text-gray-700 dark:text-gray-300 cursor-pointer flex-1"
          >
            <span className="font-medium">
              {direccion.alias || 'Dirección'}
              {direccion.es_principal && (
                <span className="ml-1 text-xs text-green-600 dark:text-green-400">
                  (Principal)
                </span>
              )}
            </span>
            <span className="block text-gray-500 dark:text-gray-400">
              {direccion.linea1}
            </span>
          </label>
        </div>
      ))}

      {/* Link to add more addresses */}
      <a
        href="/perfil"
        target="_blank"
        rel="noopener noreferrer"
        className="block text-xs text-primary-600 hover:text-primary-700 dark:text-primary-400"
      >
        + Agregar nueva dirección
      </a>
    </div>
  )
}

export default AddressSelector