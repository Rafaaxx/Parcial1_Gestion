/**
 * Textarea component
 */

import React from 'react'

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className = '', label, error, ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1">
        {label && <label className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</label>}
        <textarea
          ref={ref}
          className={`
            px-3 py-2 border rounded-md transition-colors
            bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-50
            border-gray-300 dark:border-gray-700
            hover:border-gray-400 dark:hover:border-gray-600
            focus:outline-none focus:ring-2 focus:ring-sky-500
            disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed
            resize-none
            ${error ? 'border-red-500 focus:ring-red-500' : ''}
            ${className}
          `}
          {...props}
        />
        {error && <span className="text-sm text-red-500">{error}</span>}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'
