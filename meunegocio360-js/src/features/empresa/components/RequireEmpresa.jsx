import { Navigate, Outlet } from 'react-router'
import { PERFIS } from '../../../shared/lib/perfis.js'
import { useAuth } from '../../auth'
import { useEmpresa } from '../hooks/useEmpresa.js'
import AguardandoEmpresaPage from '../pages/AguardandoEmpresaPage.jsx'

/**
 * Guarda das rotas de negócio (RF-FE-002): exige empresa ativa. Sem ela, o ADMIN vai ao
 * primeiro cadastro e os demais perfis veem "Aguardando o cadastro da empresa".
 */
export default function RequireEmpresa() {
  const { estado } = useEmpresa()
  const { usuario } = useAuth()

  if (estado === 'ativa') return <Outlet />
  if (usuario.perfil === PERFIS.ADMIN)
    return <Navigate to="/empresa/cadastro" replace />
  return <AguardandoEmpresaPage />
}
