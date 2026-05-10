/**
 * Footer component
 */

import React from 'react'

const footerLinks = [
  { label: 'Inicio', href: '/' },
  { label: 'Catálogo', href: '/productos' },
  { label: 'Contacto', href: '#' },
]

export const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-100 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            &copy; 2026 Food Store. Todos los derechos reservados.
          </p>
          <nav className="flex items-center gap-6">
            {footerLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-50 transition-colors"
              >
                {link.label}
              </a>
            ))}
          </nav>
        </div>
      </div>
    </footer>
  )
}

export default Footer
