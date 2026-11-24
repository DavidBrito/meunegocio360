import { ApiError, configureAuth, refreshOnce } from '../../shared/lib/http'
import * as authApi from './api/authApi.js'

const ANTECEDENCIA_RENOVACAO_S = 60

export const ESTADO_INICIAL = { status: 'carregando', usuario: null }

/**
 * Ciclo de vida da sessão (RF-FE-001, "Ciclo de vida da sessão"). O token de acesso vive
 * apenas nesta closure (memória): nunca em localStorage/sessionStorage (RNF-FE-12). O refresh
 * token é cookie HttpOnly, inacessível ao JavaScript.
 */
export function createSessionManager({ onChange, onCleared }) {
  let accessToken = null
  let renovacaoTimer = null

  function limpar() {
    accessToken = null
    clearTimeout(renovacaoTimer)
  }

  function encerrar({ expirou, saiu = false }) {
    limpar()
    onChange({ status: 'anonimo', usuario: null, expirou, saiu })
    onCleared()
  }

  function agendarRenovacao(expiresIn) {
    clearTimeout(renovacaoTimer)
    const ms = Math.max(expiresIn - ANTECEDENCIA_RENOVACAO_S, 5) * 1000
    renovacaoTimer = setTimeout(async () => {
      try {
        await refreshOnce()
      } catch (erro) {
        if (erro instanceof ApiError && erro.status === 401)
          encerrar({ expirou: true })
      }
    }, ms)
  }

  function aplicar(sessao) {
    accessToken = sessao.accessToken
    agendarRenovacao(sessao.expiresIn)
    onChange({ status: 'autenticado', usuario: sessao.usuario })
  }

  return {
    /** Registra a sessão na camada HTTP (renovação em 401 e token em memória). */
    conectar() {
      configureAuth({
        getToken: () => accessToken,
        refresh: async () => {
          const sessao = await authApi.refresh()
          aplicar(sessao)
          return sessao
        },
        onAuthFailure: () => encerrar({ expirou: true }),
      })
    },

    desconectar() {
      clearTimeout(renovacaoTimer)
    },

    /** Restaura a sessão na inicialização. Só 401 vira "anônimo"; rede/5xx vira "erro". */
    async restaurar() {
      onChange(ESTADO_INICIAL)
      try {
        await refreshOnce()
      } catch (erro) {
        limpar()
        if (erro instanceof ApiError && erro.status === 401) {
          onChange({ status: 'anonimo', usuario: null })
        } else {
          onChange({ status: 'erro', usuario: null })
        }
      }
    },

    entrar: aplicar,

    async sair() {
      try {
        await authApi.logout()
      } catch {
        // o resultado do logout é ignorado em caso de falha (RF-FE-001, item 5)
      }
      encerrar({ expirou: false, saiu: true }) // saída voluntária: não preserva a rota de origem
    },
  }
}
