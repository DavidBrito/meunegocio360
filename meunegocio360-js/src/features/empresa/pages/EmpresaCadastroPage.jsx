import { useState } from 'react'
import { Navigate } from 'react-router'
import EmpresaForm from '../components/EmpresaForm.jsx'
import EmpresasInativas from '../components/EmpresasInativas.jsx'
import { useEmpresa } from '../hooks/useEmpresa.js'

/** Primeiro cadastro (ADMIN, somente sem empresa ativa). Com empresa ativa, vai a /empresa. */
export default function EmpresaCadastroPage() {
  const { estado } = useEmpresa()
  // Para onde ir quando a empresa passar a existir: definido ANTES da requisição, pois o
  // cache atualiza antes de o envio resolver e esta tela já teria redirecionado ao padrão.
  const [destino, setDestino] = useState({ to: '/empresa', state: null })

  if (estado === 'ativa')
    return <Navigate to={destino.to} replace state={destino.state} />

  return (
    <>
      <title>Cadastre sua empresa — MeuNegócio360</title>
      <h1 className="h2">Cadastre sua empresa</h1>
      <p>
        Para começar, informe os dados da empresa. Ela é o contexto de clientes,
        fornecedores, produtos e demais cadastros.
      </p>
      <EmpresaForm
        aoEnviar={() =>
          setDestino({
            to: '/',
            state: { mensagem: 'Empresa cadastrada com sucesso.' },
          })
        }
      />
      <EmpresasInativas
        aoReativar={() =>
          setDestino({
            to: '/empresa',
            state: { mensagem: 'Empresa reativada com sucesso.' },
          })
        }
      />
    </>
  )
}
