import Alert from 'react-bootstrap/Alert'
import Button from 'react-bootstrap/Button'

/**
 * Alerta de erro anunciado a leitores de tela (`role="alert"`, RNF-FE-22). A mensagem nunca é
 * um texto técnico do servidor (RNF-FE-29). `acao` = { rotulo, aoClicar, desabilitado }.
 */
export default function ErrorAlert({ children, acao = null, className = '' }) {
  return (
    <Alert variant="danger" className={className}>
      <div>{children}</div>
      {acao && (
        <Button
          variant="outline-dark"
          size="sm"
          className="mt-2"
          onClick={acao.aoClicar}
          disabled={acao.desabilitado}
        >
          {acao.rotulo}
        </Button>
      )}
    </Alert>
  )
}
