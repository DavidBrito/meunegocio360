/**
 * Redirecionamento aberto: só caminhos internos são aceitos ("/algo", nunca "//host" nem
 * "/\host"). Aceita string ou objeto `location` do React Router.
 */
export function safeRedirectPath(from) {
  const path =
    typeof from === 'string'
      ? from
      : from
        ? `${from.pathname ?? ''}${from.search ?? ''}${from.hash ?? ''}`
        : ''
  const interno =
    path.startsWith('/') && !path.startsWith('//') && !path.startsWith('/\\')
  return interno && !path.startsWith('/login') ? path : '/'
}
