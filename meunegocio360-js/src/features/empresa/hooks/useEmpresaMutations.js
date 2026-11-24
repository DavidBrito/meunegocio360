import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as empresaApi from '../api/empresaApi.js'

export const CHAVE_EMPRESA = ['empresa']
export const CHAVE_INATIVAS = ['empresas-inativas']

/** Cadastro (sem `empresa`) ou edição (com `empresa`; envia a `versao` lida, RNF-BE-28). */
export function useSalvarEmpresa(empresa) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload) =>
      empresa
        ? empresaApi.atualizarEmpresa({
            id: empresa.id,
            versao: empresa.versao,
            ...payload,
          })
        : empresaApi.cadastrarEmpresa(payload),
    onSuccess: (salva) => {
      queryClient.setQueryData(CHAVE_EMPRESA, salva)
    },
  })
}

/** Inativa ou reativa. Inativada => estado "ausente" (as guardas bloqueiam as telas de negócio). */
export function useAlterarSituacao() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: empresaApi.alterarSituacaoEmpresa,
    onSuccess: (empresa) => {
      queryClient.setQueryData(CHAVE_EMPRESA, empresa.ativa ? empresa : null)
      queryClient.invalidateQueries({ queryKey: CHAVE_INATIVAS })
    },
  })
}

export function useEmpresasInativas({ habilitado }) {
  return useQuery({
    queryKey: CHAVE_INATIVAS,
    queryFn: empresaApi.listarEmpresasInativas,
    enabled: habilitado,
  })
}
