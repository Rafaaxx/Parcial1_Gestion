/**
 * HomePage — Landing page with hero section and featured content
 */

import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/shared/hooks/useAuth'

const features = [
  {
    title: 'Comida fresca',
    desc: 'Ingredientes de la mejor calidad, preparados al momento.',
    icon: '🥗',
  },
  {
    title: 'Pedidos online',
    desc: 'Hacé tu pedido desde cualquier lugar y pasá a retirar.',
    icon: '📱',
  },
  {
    title: 'Personalizá tu plato',
    desc: 'Elegí ingredientes, ajustá porciones, sin límites.',
    icon: '🎨',
  },
  {
    title: 'Entrega rápida',
    desc: 'En menos de 30 minutos tu pedido está listo.',
    icon: '⚡',
  },
]

export const HomePage: React.FC = () => {
  const { isAuthenticated } = useAuth()

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary-600 via-primary-500 to-primary-400 dark:from-primary-800 dark:via-primary-700 dark:to-primary-600 text-white">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />
        <div className="relative px-8 py-16 md:py-24 md:px-12">
          <div className="max-w-2xl">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Bienvenido a Food Store
            </h1>
            <p className="text-lg md:text-xl text-primary-100 mb-8">
              La mejor comida, al mejor precio. Pedí online y retirá cuando quieras.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link
                to="/productos"
                className="inline-flex items-center px-6 py-3 bg-white text-primary-600 font-semibold rounded-lg hover:bg-primary-50 transition-colors shadow-lg"
              >
                Ver Catálogo
              </Link>
              {!isAuthenticated && (
                <Link
                  to="/auth/register"
                  className="inline-flex items-center px-6 py-3 bg-white/20 text-white font-semibold rounded-lg hover:bg-white/30 transition-colors backdrop-blur-sm"
                >
                  Registrarse
                </Link>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50 mb-8 text-center">
          ¿Por qué elegirnos?
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="card-base p-6 hover:shadow-md transition-shadow"
            >
              <span className="text-4xl block mb-4">{feature.icon}</span>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      {isAuthenticated && (
        <section className="text-center py-12 bg-gray-50 dark:bg-gray-800/50 rounded-2xl">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50 mb-4">
            ¿Listo para pedir?
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Explorá nuestro catálogo y armá tu pedido.
          </p>
          <Link
            to="/productos"
            className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors"
          >
            Ir al Catálogo
          </Link>
        </section>
      )}
    </div>
  )
}

export default HomePage
