import { useQuery } from '@tanstack/react-query'
import { useMemo } from 'react'
import Button from 'react-bootstrap/Button'
import Container from 'react-bootstrap/Container'
import PageLoading from '../../../shared/ui/PageLoading.jsx'
import { useAuth } from '../../auth'
import { obterEmpresaAtiva } from '../api/empresaApi.js'
import { EmpresaContext } from '../context/EmpresaContext.js'
import { CHAVE_EMPRESA } from '../hooks/useEmpresaMutations.js'

/**
 * Empresa ativa e parâmetros de exibição, consultada UMA vez por sessão (TanStack Query).
 * Estados: `carregando` | `ativa` | `ausente` (404 COMPANY_NOT_REGISTERED) | `erro`.
 * Enquanto carrega ou em erro, nenhuma tela protegida é renderizada (sem "flash", RF-FE-002).
 */
export default function EmpresaProvider({ children }) {
  const { sair } = useAuth()
  const consulta = useQuery({
    queryKey: CHAVE_EMPRESA,
    queryFn: obterEmpresaAtiva,
    staleTime: Infinity,
    refetchOnWindowFocus: false,
  })

  const valor = useMemo(
    () => ({
      estado: consulta.data ? 'ativa' : 'ausente',
      empresa: consulta.data ?? null,
      recarregar: consulta.refetch,
    }),
    [consulta.data, consulta.refetch],
  )

  if (consulta.isPending) return <PageLoading />

  if (consulta.isError) {
    return (
      <Container
        as="main"
        className="min-vh-100 d-flex align-items-center justify-content-center"
      >
        <title>Erro de conexão — MeuNegócio360</title>
        <div role="alert" className="alert alert-danger text-center mb-0">
          <h1 className="h4">Não foi possível carregar os dados da empresa</h1>
          <p>Verifique sua conexão e tente novamente.</p>
          <div className="d-flex gap-2 justify-content-center">
            <Button variant="primary" onClick={() => consulta.refetch()}>
              Tentar novamente
            </Button>
            <Button variant="outline-dark" onClick={sair}>
              Sair
            </Button>
          </div>
        </div>
      </Container>
    )
  }

  return <EmpresaContext value={valor}>{children}</EmpresaContext>
}
