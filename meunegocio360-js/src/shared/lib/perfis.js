// Perfis de acesso: única fonte no frontend (RF-FE-002); nunca escritos como texto solto.
export const PERFIS = Object.freeze({
  ADMIN: 'ADMIN',
  OPERADOR_COMERCIAL: 'OPERADOR_COMERCIAL',
  OPERADOR_FINANCEIRO: 'OPERADOR_FINANCEIRO',
})

export const TODOS_OS_PERFIS = Object.freeze(Object.values(PERFIS))

export const ROTULOS_PERFIL = Object.freeze({
  [PERFIS.ADMIN]: 'Administrador',
  [PERFIS.OPERADOR_COMERCIAL]: 'Operador comercial',
  [PERFIS.OPERADOR_FINANCEIRO]: 'Operador financeiro',
})
