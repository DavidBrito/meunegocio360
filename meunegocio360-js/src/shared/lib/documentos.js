// Máscaras e validações de documentos (RNF-FE-28). Funções únicas, sem pacote adicional
// (RNF-015): a API recebe CNPJ e telefone somente com dígitos.

export const somenteDigitos = (valor = '') => String(valor).replace(/\D/g, '')

export function mascaraCnpj(valor) {
  const d = somenteDigitos(valor).slice(0, 14)
  if (d.length > 12)
    return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5, 8)}/${d.slice(8, 12)}-${d.slice(12)}`
  if (d.length > 8)
    return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5, 8)}/${d.slice(8)}`
  if (d.length > 5) return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5)}`
  if (d.length > 2) return `${d.slice(0, 2)}.${d.slice(2)}`
  return d
}

const PESOS_CNPJ_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
const PESOS_CNPJ_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

function digitoCnpj(base, pesos) {
  const soma = pesos.reduce((acc, peso, i) => acc + Number(base[i]) * peso, 0)
  const resto = soma % 11
  return resto < 2 ? 0 : 11 - resto
}

/** CNPJ só com dígitos: 14 posições, dígitos verificadores corretos, sem sequência repetida. */
export function validarCnpj(digitos) {
  if (!/^\d{14}$/.test(digitos) || digitos === digitos[0].repeat(14))
    return false
  const primeiro = digitoCnpj(digitos, PESOS_CNPJ_1)
  const segundo = digitoCnpj(digitos.slice(0, 12) + primeiro, PESOS_CNPJ_2)
  return digitos.slice(12) === `${primeiro}${segundo}`
}

export function mascaraTelefone(valor) {
  const d = somenteDigitos(valor).slice(0, 11)
  if (d.length > 6) {
    const corte = d.length > 10 ? 7 : 6
    return `(${d.slice(0, 2)}) ${d.slice(2, corte)}-${d.slice(corte)}`
  }
  if (d.length > 2) return `(${d.slice(0, 2)}) ${d.slice(2)}`
  return d
}

/** Telefone com DDD: 10 ou 11 dígitos. */
export const validarTelefone = (digitos) => /^\d{10,11}$/.test(digitos)

export const emailValido = (valor) => /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(valor)
