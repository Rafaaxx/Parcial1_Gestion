/**
 * CancelarPedidoModal - Modal para confirmar cancelación de pedido con motivo obligatorio
 */

import { useState } from 'react'
import { Modal } from '@/shared/ui/Modal'
import { Textarea } from '@/shared/ui/Textarea'
import { Button } from '@/shared/ui/Button'

interface CancelarPedidoModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: (motivo: string) => void
  isLoading?: boolean
}

export function CancelarPedidoModal({
  isOpen,
  onClose,
  onConfirm,
  isLoading = false,
}: CancelarPedidoModalProps) {
  const [motivo, setMotivo] = useState('')
  const [error, setError] = useState('')

  const handleConfirm = () => {
    if (!motivo.trim()) {
      setError('El motivo es obligatorio')
      return
    }
    setError('')
    onConfirm(motivo.trim())
  }

  const handleClose = () => {
    setMotivo('')
    setError('')
    onClose()
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Cancelar Pedido"
    >
      <div className="space-y-4">
        <p className="text-gray-600 dark:text-gray-300">
          ¿Estás seguro de que deseas cancelar este pedido? Esta acción no se puede deshacer.
        </p>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Motivo de cancelación <span className="text-red-500">*</span>
          </label>
          <Textarea
            value={motivo}
            onChange={(e) => {
              setMotivo(e.target.value)
              if (error) setError('')
            }}
            placeholder="Ej: Ya no lo necesito, cambiaron los planes..."
            rows={3}
            error={error}
          />
          {error && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>}
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={isLoading}
          >
            Mantener Pedido
          </Button>
          <Button
            variant="danger"
            onClick={handleConfirm}
            disabled={isLoading}
          >
            {isLoading ? 'Cancelando...' : 'Confirmar Cancelación'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}