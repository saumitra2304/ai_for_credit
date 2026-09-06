import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { applyTheme, getTheme } from '@/lib/theme'
import './index.css'
import App from './App.jsx'

applyTheme(getTheme())

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
