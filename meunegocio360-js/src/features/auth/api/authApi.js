import { request } from '../../../shared/lib/http'

// Contrato do RF-BE-001. As três chamadas usam `auth: false`: não levam Bearer e nunca
// disparam a renovação automática (evita laço infinito de /auth/refresh).
export const login = (credenciais) =>
  request('/auth/login', { method: 'POST', body: credenciais, auth: false })

export const refresh = () =>
  request('/auth/refresh', { method: 'POST', auth: false })

export const logout = () =>
  request('/auth/logout', { method: 'POST', auth: false })
