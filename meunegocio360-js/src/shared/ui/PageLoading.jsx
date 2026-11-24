import Spinner from 'react-bootstrap/Spinner'

/** Indicador de carregamento de página inteira, acessível (`role="status"`, RNF-062). */
export default function PageLoading() {
  return (
    <div
      role="status"
      className="min-vh-100 d-flex flex-column align-items-center justify-content-center gap-2"
    >
      <Spinner animation="border" aria-hidden="true" />
      <span>Carregando…</span>
    </div>
  )
}
