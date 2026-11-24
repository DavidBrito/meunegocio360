import { ApiError } from './ApiError.js'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'
const TIMEOUT_MS = 15_000

// A feature de autenticação se registra aqui (`shared` não importa de `features`, RNF-FE-01).
let authBridge = {
  getToken: () => null,
  refresh: async () => {
    throw new Error('Autenticação não configurada')
  },
  onAuthFailure: () => {},
}

export function configureAuth(bridge) {
  authBridge = { ...authBridge, ...bridge }
}

let refreshInFlight = null

/**
 * Renovação de sessão *single-flight* (RNF-FE-15): chamadas simultâneas compartilham UMA
 * requisição a /auth/refresh. O refresh token é rotativo; duas chamadas paralelas com o
 * mesmo cookie derrubariam a sessão (detecção de reuso do backend). Também absorve a
 * dupla execução de efeitos do StrictMode em desenvolvimento.
 */
export function refreshOnce() {
  refreshInFlight ??= authBridge.refresh().finally(() => {
    refreshInFlight = null
  })
  return refreshInFlight
}

function newRequestId() {
  return (
    globalThis.crypto?.randomUUID?.() ??
    `${Date.now()}-${Math.random().toString(16).slice(2)}`
  )
}

async function toApiError(response) {
  const retryAfter = Number.parseInt(
    response.headers.get('Retry-After') ?? '',
    10,
  )
  let problem = null
  if ((response.headers.get('Content-Type') ?? '').includes('json')) {
    problem = await response.json().catch(() => null)
  }
  return new ApiError({
    status: response.status,
    code: problem?.code ?? 'HTTP_ERROR',
    detail: problem?.detail,
    errors: problem?.errors ?? [],
    traceId: problem?.traceId ?? null,
    retryAfter: Number.isNaN(retryAfter) ? null : retryAfter,
  })
}

async function send(path, { method, body, signal }, token) {
  const controller = new AbortController()
  const timer = setTimeout(
    () => controller.abort(new DOMException('Tempo esgotado', 'TimeoutError')),
    TIMEOUT_MS,
  )
  signal?.addEventListener('abort', () => controller.abort(signal.reason), {
    once: true,
  })

  const headers = { Accept: 'application/json', 'X-Request-Id': newRequestId() }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`

  try {
    return await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
      credentials: 'same-origin', // envia o cookie de refresh nas chamadas /auth/* (RNF-FE-10)
    })
  } catch (error) {
    const timeout =
      error?.name === 'TimeoutError' ||
      controller.signal.reason?.name === 'TimeoutError'
    throw new ApiError({
      status: 0,
      code: timeout ? 'TIMEOUT' : 'NETWORK_ERROR',
      detail: 'Não foi possível se comunicar com o servidor.',
    })
  } finally {
    clearTimeout(timer)
  }
}

/**
 * Cliente HTTP único (RNF-FE-03/10/11).
 * - `auth` (padrão true): injeta `Authorization: Bearer` e trata `401` com UMA renovação
 *   e repetição da requisição. Chamadas /auth/* usam `auth: false`, o que também impede o
 *   laço infinito de renovação (o refresh nunca entra no fluxo "renovar e repetir").
 */
export async function request(
  path,
  { method = 'GET', body, auth = true, signal } = {},
) {
  const options = { method, body, signal }
  let response = await send(path, options, auth ? authBridge.getToken() : null)

  if (response.status === 401 && auth) {
    let session
    try {
      session = await refreshOnce()
    } catch (refreshError) {
      // Só um 401 na renovação encerra a sessão; falha de rede não derruba quem está logado.
      if (refreshError instanceof ApiError && refreshError.status === 401)
        authBridge.onAuthFailure(refreshError)
      throw await toApiError(response)
    }
    response = await send(path, options, session.accessToken)
  }

  if (!response.ok) throw await toApiError(response)
  if (response.status === 204) return null
  return response.json()
}
