import Alert from 'react-bootstrap/Alert'
import Button from 'react-bootstrap/Button'

/** Falha de rede/5xx ao restaurar a sessão: NÃO é sessão inválida (RF-FE-001). */
export default function SessionRestoreError({ onRetry }) {
  return (
    <main className="container min-vh-100 d-flex align-items-center justify-content-center py-4">
      <title>Erro de conexão — MeuNegócio360</title>
      <Alert variant="danger" className="text-center mb-0">
        <h1 className="h4">Não foi possível verificar sua sessão</h1>
        <p>Verifique sua conexão e tente novamente. Nenhum dado foi perdido.</p>
        <Button variant="primary" onClick={onRetry}>
          Tentar novamente
        </Button>
      </Alert>
    </main>
  )
}
