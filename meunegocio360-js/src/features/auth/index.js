// API pública da feature (RNF-FE-01): outras partes do app importam só daqui.
import { lazy } from 'react'

export { default as AuthProvider } from './components/AuthProvider.jsx'
export { default as PublicOnly } from './components/PublicOnly.jsx'
export { default as RequireAuth } from './components/RequireAuth.jsx'
export { useAuth } from './hooks/useAuth.js'

export const LoginPage = lazy(() => import('./pages/LoginPage.jsx'))
