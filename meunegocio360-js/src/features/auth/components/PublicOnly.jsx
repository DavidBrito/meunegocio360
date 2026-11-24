import { Navigate, Outlet, useLocation } from 'react-router'
import { safeRedirectPath } from '../../../shared/lib/safeRedirect.js'
import PageLoading from '../../../shared/ui/PageLoading.jsx'
import { useAuth } from '../hooks/useAuth.js'
import SessionRestoreError from './SessionRestoreError.jsx'

/** Rotas só para anônimos (/login): quem já tem sessão vai para a rota de origem ou `/`. */
export default function PublicOnly() {
  const { status, tentarRestaurarNovamente } = useAuth()
  const location = useLocation()

  if (status === 'carregando') return <PageLoading />
  if (status === 'erro')
    return <SessionRestoreError onRetry={tentarRestaurarNovamente} />
  if (status === 'autenticado') {
    return <Navigate to={safeRedirectPath(location.state?.from)} replace />
  }
  return <Outlet />
}
