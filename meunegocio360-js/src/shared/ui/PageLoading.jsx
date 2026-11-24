import Spinner from 'react-bootstrap/Spinner'

/** Indicador de carregamento acessível (`role="status"`, RNF-062). `compacto` = dentro do layout. */
export default function PageLoading({ compacto = false }) {
  return (
    <div
      role="status"
      className={`${compacto ? 'py-5' : 'min-vh-100'} d-flex flex-column align-items-center justify-content-center gap-2`}
    >
      <Spinner animation="border" aria-hidden="true" />
      <span>Carregando…</span>
    </div>
  )
}
