import React from 'react'
import ReactDOM from 'react-dom/client'
import { App } from '@/app/App'
import '@/index.css'
// Import HTTP interceptors to set them up
import '@/shared/http'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
