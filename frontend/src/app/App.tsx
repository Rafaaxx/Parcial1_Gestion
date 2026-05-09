/**
 * Root App component with providers and theme support
 */

import React, { useEffect } from 'react'
import { useTheme } from '@/shared/hooks'

export const App: React.FC = () => {
  const { theme, applyTheme } = useTheme()

  // Apply theme on mount and when it changes
  useEffect(() => {
    applyTheme(theme)
  }, [theme, applyTheme])

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark' : ''}`}>
      <main className="bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-50 min-h-screen">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold mb-8">Food Store - Frontend Setup Complete ✅</h1>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Welcome Card */}
            <div className="bg-gradient-to-br from-sky-50 to-sky-100 dark:from-gray-800 dark:to-gray-900 rounded-lg p-6 border border-sky-200 dark:border-gray-700">
              <h2 className="text-2xl font-semibold mb-3">Welcome to Food Store</h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                This is the foundation of our frontend. All infrastructure is ready for future features.
              </p>
              <div className="flex gap-2">
                <span className="px-3 py-1 bg-sky-500 text-white rounded-full text-sm">React 19</span>
                <span className="px-3 py-1 bg-sky-500 text-white rounded-full text-sm">TypeScript</span>
                <span className="px-3 py-1 bg-sky-500 text-white rounded-full text-sm">Zustand</span>
              </div>
            </div>

            {/* Stack Card */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-gray-800 dark:to-gray-900 rounded-lg p-6 border border-green-200 dark:border-gray-700">
              <h2 className="text-2xl font-semibold mb-3">Tech Stack</h2>
              <ul className="space-y-2 text-gray-700 dark:text-gray-300">
                <li>✓ Vite for blazing fast builds</li>
                <li>✓ Zustand for state management</li>
                <li>✓ Tailwind CSS for styling</li>
                <li>✓ Axios for API calls</li>
                <li>✓ TypeScript for type safety</li>
                <li>✓ FSD architecture</li>
              </ul>
            </div>
          </div>

          {/* Features Section */}
          <div className="mt-12">
            <h2 className="text-2xl font-semibold mb-6">Available Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { title: 'Authentication Store', desc: 'User, token management ready' },
                { title: 'UI Store', desc: 'Theme, toast notifications' },
                { title: 'HTTP Client', desc: 'Axios with interceptors' },
                { title: 'UI Components', desc: 'Button, Card, Modal, Input...' },
                { title: 'Custom Hooks', desc: 'useAuth, useTheme, useLocalStorage' },
                { title: 'Utilities', desc: 'Formatters, validators, storage' },
              ].map((feature) => (
                <div key={feature.title} className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
                  <h3 className="font-semibold mb-2">{feature.title}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Next Steps */}
          <div className="mt-12 bg-blue-50 dark:bg-gray-800 rounded-lg p-6 border border-blue-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold mb-4">Next Steps</h2>
            <ol className="list-decimal list-inside space-y-2 text-gray-700 dark:text-gray-300">
              <li>CHANGE-00c: Add CORS + Rate Limiting to backend</li>
              <li>CHANGE-00d: Add seed data + base tests</li>
              <li>CHANGE-01: Implement Authentication (Login/Register)</li>
              <li>CHANGE-02: Add navigation and layout with role-based UI</li>
              <li>...and 13 more changes to build complete Food Store</li>
            </ol>
          </div>
        </div>
      </main>
    </div>
  )
}
