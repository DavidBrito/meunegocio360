import Container from 'react-bootstrap/Container'
import { Link } from 'react-router'

export default function NotFoundPage() {
  return (
    <Container
      as="main"
      className="min-vh-100 d-flex flex-column align-items-center justify-content-center text-center"
    >
      <title>Página não encontrada — MeuNegócio360</title>
      <h1>Página não encontrada</h1>
      <p>O endereço acessado não existe.</p>
      <Link to="/">Ir para a página inicial</Link>
    </Container>
  )
}
