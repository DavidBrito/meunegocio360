import { Outlet } from 'react-router'
import AcessoNegadoPage from '../pages/AcessoNegadoPage.jsx'
import { useAuth } from '../hooks/useAuth.js'

/**
 * Guarda por perfil (RNF-FE-16, RNF-FE-13): perfil sem permissão vê "Acesso negado" e nenhuma
 * requisição de dados é feita. É só UX; a autorização real é do backend (RNF-BE-47).
 */
export default function RequireRole({ perfis }) {
  const { usuario } = useAuth()
  return perfis.includes(usuario.perfil) ? <Outlet /> : <AcessoNegadoPage />
}
