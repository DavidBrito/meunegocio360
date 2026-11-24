import { ApiError, request } from '../../../shared/lib/http'

/** Empresa ativa, ou `null` quando não há (404 COMPANY_NOT_REGISTERED não é erro, RF-FE-002). */
export async function obterEmpresaAtiva() {
  try {
    return await request('/empresa')
  } catch (erro) {
    if (erro instanceof ApiError && erro.code === 'COMPANY_NOT_REGISTERED')
      return null
    throw erro
  }
}

// Empresas inativas (adendo do fork ao RF-BE-002): a mais recentemente inativada primeiro.
export const listarEmpresasInativas = () =>
  request('/empresa/inativas?size=50&sort=atualizadoEm,desc')

export const cadastrarEmpresa = (dados) =>
  request('/empresa', { method: 'POST', body: dados })

export const atualizarEmpresa = ({ id, ...dados }) =>
  request(`/empresa/${id}`, { method: 'PUT', body: dados })

export const alterarSituacaoEmpresa = ({ id, ativa, versao }) =>
  request(`/empresa/${id}/situacao`, {
    method: 'PATCH',
    body: { ativa, versao },
  })
