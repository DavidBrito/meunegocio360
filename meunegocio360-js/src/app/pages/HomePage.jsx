import Button from 'react-bootstrap/Button'
import Card from 'react-bootstrap/Card'
import Container from 'react-bootstrap/Container'
import { useAuth } from '../../features/auth'

/** Página inicial provisória (será substituída pelo dashboard). */
export default function HomePage() {
  const { usuario, sair } = useAuth()

  return (
    <>
      <title>Início — MeuNegócio360</title>
      <header className="text-bg-primary py-2">
        <Container className="d-flex align-items-center justify-content-between">
          <p className="h4 mb-0">MeuNegócio360</p>
          <Button variant="outline-dark" onClick={sair}>
            Sair
          </Button>
        </Container>
      </header>
      <Container as="main" className="py-4">
        <Card>
          <Card.Body>
            <h1 className="h2">Olá, {usuario.nome}</h1>
            <p className="mb-0">
              Perfil: <strong>{usuario.perfil}</strong>
            </p>
          </Card.Body>
        </Card>
      </Container>
    </>
  )
}
