import { useContext } from 'react'
import { EmpresaContext } from '../context/EmpresaContext.js'

export function useEmpresa() {
  const contexto = useContext(EmpresaContext)
  if (!contexto)
    throw new Error('useEmpresa deve ser usado dentro de <EmpresaProvider>')
  return contexto
}
