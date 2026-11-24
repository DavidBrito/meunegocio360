import { useState } from 'react'
import Button from 'react-bootstrap/Button'
import ListGroup from 'react-bootstrap/ListGroup'
import Spinner from 'react-bootstrap/Spinner'
import { mascaraCnpj } from '../../../shared/lib/documentos.js'
import ErrorAlert from '../../../shared/ui/ErrorAlert.jsx'
import {
  useAlterarSituacao,
  useEmpresasInativas,
} from '../hooks/useEmpresaMutations.js'

const formatarData = (iso) => new Date(iso).toLocaleDateString('pt-BR')

/**
 * Empresas inativas, para o ADMIN reativar (adendo do fork: GET /empresa/inativas). Como
 * `GET /empresa` só devolve a ativa, esta lista é o único caminho de volta após inativar.
 */
export default function EmpresasInativas({ aoReativar }) {
  const consulta = useEmpresasInativas({ habilitado: true })
  const alterar = useAlterarSituacao()
  const [erro, setErro] = useState(null)

  async function reativar(empresa) {
    setErro(null)
    aoReativar?.()
    try {
      await alterar.mutateAsync({
        id: empresa.id,
        ativa: true,
        versao: empresa.versao,
      })
    } catch (falha) {
      setErro(
        falha.code === 'COMPANY_ALREADY_ACTIVE'
          ? 'Já existe uma empresa ativa. Inative-a antes de cadastrar ou reativar outra.'
          : falha.code === 'VERSION_CONFLICT'
            ? 'Esta empresa foi alterada por outra pessoa. Atualize a lista e tente novamente.'
            : 'Não foi possível reativar a empresa agora. Tente novamente.',
      )
      if (falha.code === 'VERSION_CONFLICT') consulta.refetch()
    }
  }

  if (consulta.isPending) {
    return (
      <div role="status" className="d-flex align-items-center gap-2">
        <Spinner animation="border" size="sm" aria-hidden="true" />
        <span>Carregando empresas inativas…</span>
      </div>
    )
  }
  if (consulta.isError) {
    return (
      <ErrorAlert
        acao={{
          rotulo: 'Tentar novamente',
          aoClicar: () => consulta.refetch(),
        }}
      >
        Não foi possível carregar as empresas inativas.
      </ErrorAlert>
    )
  }
  const itens = consulta.data.content
  if (itens.length === 0) return null

  return (
    <section aria-labelledby="titulo-inativas" className="mt-5">
      <h2 id="titulo-inativas" className="h4">
        Empresas inativas
      </h2>
      <p>
        Se preferir, reative uma empresa já cadastrada em vez de cadastrar
        outra.
      </p>
      {erro && <ErrorAlert className="mb-3">{erro}</ErrorAlert>}
      <ListGroup>
        {itens.map((empresa) => (
          <ListGroup.Item
            key={empresa.id}
            className="d-flex flex-wrap align-items-center justify-content-between gap-2"
          >
            <div>
              <strong>{empresa.nomeFantasia || empresa.razaoSocial}</strong>
              <div className="small text-body-secondary">
                CNPJ {mascaraCnpj(empresa.cnpj)} · inativada em{' '}
                {formatarData(empresa.atualizadoEm)}
              </div>
            </div>
            <Button
              variant="outline-dark"
              onClick={() => reativar(empresa)}
              disabled={alterar.isPending}
              aria-label={`Reativar ${empresa.nomeFantasia || empresa.razaoSocial}`}
            >
              {alterar.isPending && alterar.variables?.id === empresa.id
                ? 'Reativando…'
                : 'Reativar'}
            </Button>
          </ListGroup.Item>
        ))}
      </ListGroup>
    </section>
  )
}
