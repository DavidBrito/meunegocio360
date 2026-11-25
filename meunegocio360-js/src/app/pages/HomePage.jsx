import { useState } from 'react'
import Alert from 'react-bootstrap/Alert'
import Card from 'react-bootstrap/Card'
import { useLocation } from 'react-router'
import { useAuth } from '../../features/auth'
import { ROTULOS_PERFIL } from '../../shared/lib/perfis.js'

/** Página inicial provisória (será substituída pelo dashboard). Dentro do AppLayout. */
export default function HomePage() {
  const { usuario } = useAuth()
  const location = useLocation()
  const [mensagem, setMensagem] = useState(location.state?.mensagem ?? null)

  return (
    <>
      <title>Início — MeuNegócio360</title>
      {mensagem && (
        <Alert variant="success" dismissible onClose={() => setMensagem(null)}>
          {mensagem}
        </Alert>
      )}
      <Card>
        <Card.Body>
          <h1 className="h2">Olá, {usuario.nome}</h1>
          <p className="mb-0">
            Perfil: <strong>{ROTULOS_PERFIL[usuario.perfil]}</strong>
          </p>
        </Card.Body>
      </Card>
    </>
  )
}
