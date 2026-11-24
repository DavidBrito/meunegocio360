import { useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'
import { AuthContext } from '../context/AuthContext.js'
import { createSessionManager, ESTADO_INICIAL } from '../sessionManager.js'

/**
 * Contexto de autenticação (RNF-FE-04). Na inicialização entra em `carregando` e tenta
 * restaurar a sessão por refresh token (cookie HttpOnly). O efeito abaixo é inicialização
 * de sessão, não busca de dados de tela; a chamada é *single-flight*, então o StrictMode
 * não gera duas renovações (RF-FE-001, pontos de atenção).
 */
export default function AuthProvider({ children }) {
  const queryClient = useQueryClient()
  const [estado, setEstado] = useState(ESTADO_INICIAL)
  const [sessao] = useState(() =>
    createSessionManager({
      onChange: setEstado,
      onCleared: () => queryClient.clear(),
    }),
  )

  useEffect(() => {
    sessao.conectar()
    sessao.restaurar()
    return () => sessao.desconectar()
  }, [sessao])

  const valor = useMemo(
    () => ({
      ...estado,
      entrar: sessao.entrar,
      sair: sessao.sair,
      tentarRestaurarNovamente: sessao.restaurar,
    }),
    [estado, sessao],
  )

  return <AuthContext value={valor}>{children}</AuthContext>
}
