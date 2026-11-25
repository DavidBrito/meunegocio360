// API pública da feature (RNF-FE-01): outras partes do app importam só daqui.
import { lazy } from 'react'

export { default as EmpresaProvider } from './components/EmpresaProvider.jsx'
export { default as RequireEmpresa } from './components/RequireEmpresa.jsx'
export { useEmpresa } from './hooks/useEmpresa.js'

export const EmpresaPage = lazy(() => import('./pages/EmpresaPage.jsx'))
export const EmpresaCadastroPage = lazy(
  () => import('./pages/EmpresaCadastroPage.jsx'),
)
