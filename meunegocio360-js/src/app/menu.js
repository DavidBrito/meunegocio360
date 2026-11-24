import { TODOS_OS_PERFIS } from '../shared/lib/perfis.js'

/**
 * Itens do menu e perfis que os veem (RF-FE-002, RNF-FE-16: só UX; a autorização real é do
 * backend). Cada RF seguinte acrescenta o seu item aqui, por exemplo:
 * { rotulo: 'Clientes', to: '/clientes', perfis: [PERFIS.ADMIN, PERFIS.OPERADOR_COMERCIAL] }.
 */
export const ITENS_MENU = [
  { rotulo: 'Início', to: '/', perfis: TODOS_OS_PERFIS },
  { rotulo: 'Empresa', to: '/empresa', perfis: TODOS_OS_PERFIS },
]

export const itensDoPerfil = (perfil) =>
  ITENS_MENU.filter((item) => item.perfis.includes(perfil))
