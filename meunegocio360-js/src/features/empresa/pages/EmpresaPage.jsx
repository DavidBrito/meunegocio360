import { useState } from 'react'
import Alert from 'react-bootstrap/Alert'
import Button from 'react-bootstrap/Button'
import Card from 'react-bootstrap/Card'
import { Navigate, useLocation } from 'react-router'
import { PERFIS } from '../../../shared/lib/perfis.js'
import ConfirmModal from '../../../shared/ui/ConfirmModal.jsx'
import ErrorAlert from '../../../shared/ui/ErrorAlert.jsx'
import { useAuth } from '../../auth'
import EmpresaDetalhes from '../components/EmpresaDetalhes.jsx'
import EmpresaForm from '../components/EmpresaForm.jsx'
import { useEmpresa } from '../hooks/useEmpresa.js'
import { useAlterarSituacao } from '../hooks/useEmpresaMutations.js'
import AguardandoEmpresaPage from './AguardandoEmpresaPage.jsx'

/** `/empresa`: leitura para todos; ADMIN edita e inativa (RF-FE-002, matriz de perfis). */
export default function EmpresaPage() {
  const { estado, empresa } = useEmpresa()
  const { usuario } = useAuth()
  const location = useLocation()
  const alterar = useAlterarSituacao()
  const [editando, setEditando] = useState(false)
  const [confirmando, setConfirmando] = useState(false)
  const [mensagem, setMensagem] = useState(location.state?.mensagem ?? null)
  const [erroInativar, setErroInativar] = useState(null)
  const admin = usuario.perfil === PERFIS.ADMIN

  if (estado !== 'ativa') {
    return admin ? (
      <Navigate to="/empresa/cadastro" replace />
    ) : (
      <AguardandoEmpresaPage />
    )
  }

  async function inativar() {
    setErroInativar(null)
    try {
      await alterar.mutateAsync({
        id: empresa.id,
        ativa: false,
        versao: empresa.versao,
      })
      // estado passa a "ausente": as guardas bloqueiam as telas de negócio e o ADMIN vai ao cadastro
    } catch (falha) {
      setConfirmando(false)
      setErroInativar(
        falha.code === 'VERSION_CONFLICT'
          ? 'Os dados da empresa foram alterados por outra pessoa. Recarregue a página e tente novamente.'
          : falha.code === 'ACCESS_DENIED'
            ? 'Você não tem permissão para alterar os dados da empresa.'
            : 'Não foi possível inativar a empresa agora. Tente novamente.',
      )
    }
  }

  return (
    <>
      <title>Empresa — MeuNegócio360</title>
      <h1 className="h2">Empresa</h1>
      {mensagem && (
        <Alert variant="success" dismissible onClose={() => setMensagem(null)}>
          {mensagem}
        </Alert>
      )}
      {erroInativar && <ErrorAlert className="mb-3">{erroInativar}</ErrorAlert>}

      <Card>
        <Card.Body>
          {editando ? (
            <EmpresaForm
              empresa={empresa}
              aoSalvar={() => {
                setEditando(false)
                setMensagem('Dados da empresa atualizados.')
              }}
              aoCancelar={() => setEditando(false)}
            />
          ) : (
            <>
              <EmpresaDetalhes empresa={empresa} />
              {admin && (
                <div className="d-flex flex-wrap gap-2 mt-4">
                  <Button variant="primary" onClick={() => setEditando(true)}>
                    Editar
                  </Button>
                  <Button
                    variant="outline-danger"
                    onClick={() => setConfirmando(true)}
                  >
                    Inativar
                  </Button>
                </div>
              )}
            </>
          )}
        </Card.Body>
      </Card>

      <ConfirmModal
        aberto={confirmando}
        titulo="Inativar a empresa?"
        rotuloConfirmar="Inativar"
        carregando={alterar.isPending}
        aoConfirmar={inativar}
        aoCancelar={() => setConfirmando(false)}
      >
        Ao inativar a empresa, não será possível cadastrar clientes,
        fornecedores, produtos nem vendas até que uma empresa seja ativada.
      </ConfirmModal>
    </>
  )
}
