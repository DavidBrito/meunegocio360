import Card from 'react-bootstrap/Card'
import Col from 'react-bootstrap/Col'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import logo from '../../../assets/logo.png'
import LoginForm from '../components/LoginForm.jsx'

export default function LoginPage() {
  return (
    <Container as="main" className="min-vh-100 d-flex align-items-center py-4">
      <title>Entrar — MeuNegócio360</title>
      <Row className="w-100 justify-content-center">
        <Col xs={12} sm={10} md={7} lg={5} xl={4}>
          <Card>
            <Card.Body className="p-4">
              {/* Logo acima dos campos (identidade da marca; o nome do produto está na imagem) */}
              <img
                src={logo}
                alt="MeuNegócio360"
                width="240"
                height="155"
                className="img-fluid d-block mx-auto mb-3"
              />
              <h1 className="h2 text-center mb-4">Entrar</h1>
              <LoginForm />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}
