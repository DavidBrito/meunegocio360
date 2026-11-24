import { Navigate, Outlet, useLocation } from 'react-router'
import PageLoading from '../../../shared/ui/PageLoading.jsx'
import { useAuth } from '../hooks/useAuth.js'
import SessionRestoreError from './SessionRestoreError.jsx'

/** Guarda de rotas protegidas (RNF-FE-13). Autorização real é do backend (UX apenas). */
export default function RequireAuth() {
  const { status, expirou, tentarRestaurarNovamente } = useAuth()
  const location = useLocation()

  // Enquanto restaura a sessão, não renderiza telas protegidas nem redireciona (sem "flash").
  if (status === 'carregando') return <PageLoading />
  if (status === 'erro')
    return <SessionRestoreError onRetry={tentarRestaurarNovamente} />
  if (status === 'anonimo') {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location, expirou: Boolean(expirou) }}
      />
    )
  }
  return <Outlet />
}
