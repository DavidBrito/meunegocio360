/**
 * Erro tipado das chamadas à API (RNF-FE-11). A decisão de comportamento usa `code`
 * (e `status`), nunca o texto da mensagem (RNF-FE-14).
 * `status === 0` indica falha de rede ou *timeout* (sem resposta do servidor).
 */
export class ApiError extends Error {
  constructor({
    status,
    code,
    detail,
    errors = [],
    traceId = null,
    retryAfter = null,
  }) {
    super(detail ?? code)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.detail = detail
    this.errors = errors
    this.traceId = traceId
    this.retryAfter = retryAfter
  }
}
