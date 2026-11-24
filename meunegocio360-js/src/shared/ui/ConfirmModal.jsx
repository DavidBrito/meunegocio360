import Button from 'react-bootstrap/Button'
import Modal from 'react-bootstrap/Modal'
import Spinner from 'react-bootstrap/Spinner'

/**
 * Confirmação de ação destrutiva. O `Modal` do react-bootstrap prende o foco, fecha com Esc
 * e devolve o foco ao botão de origem ao fechar (RNF-FE-22/23).
 */
export default function ConfirmModal({
  aberto,
  titulo,
  children,
  rotuloConfirmar = 'Confirmar',
  carregando = false,
  aoConfirmar,
  aoCancelar,
}) {
  return (
    <Modal show={aberto} onHide={carregando ? undefined : aoCancelar} centered>
      <Modal.Header closeButton={!carregando}>
        <Modal.Title as="h2" className="h4">
          {titulo}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>{children}</Modal.Body>
      <Modal.Footer>
        <Button
          variant="outline-dark"
          onClick={aoCancelar}
          disabled={carregando}
        >
          Cancelar
        </Button>
        <Button variant="danger" onClick={aoConfirmar} disabled={carregando}>
          {carregando && (
            <Spinner
              as="span"
              animation="border"
              size="sm"
              aria-hidden="true"
              className="me-2"
            />
          )}
          {rotuloConfirmar}
        </Button>
      </Modal.Footer>
    </Modal>
  )
}
