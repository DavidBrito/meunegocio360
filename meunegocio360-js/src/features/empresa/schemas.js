import { z } from 'zod'
import {
  emailValido,
  mascaraCnpj,
  mascaraTelefone,
  somenteDigitos,
  validarCnpj,
  validarTelefone,
} from '../../shared/lib/documentos.js'

// Fusos brasileiros mais UTC (RF-FE-002); o padrão é America/Sao_Paulo.
export const FUSOS_HORARIOS = [
  { valor: 'America/Sao_Paulo', rotulo: 'Brasília (America/Sao_Paulo)' },
  { valor: 'America/Noronha', rotulo: 'Fernando de Noronha (America/Noronha)' },
  { valor: 'America/Belem', rotulo: 'Pará e Amapá (America/Belem)' },
  { valor: 'America/Fortaleza', rotulo: 'Nordeste (America/Fortaleza)' },
  { valor: 'America/Recife', rotulo: 'Pernambuco (America/Recife)' },
  { valor: 'America/Bahia', rotulo: 'Bahia (America/Bahia)' },
  { valor: 'America/Cuiaba', rotulo: 'Mato Grosso (America/Cuiaba)' },
  {
    valor: 'America/Campo_Grande',
    rotulo: 'Mato Grosso do Sul (America/Campo_Grande)',
  },
  { valor: 'America/Manaus', rotulo: 'Amazonas (America/Manaus)' },
  { valor: 'America/Porto_Velho', rotulo: 'Rondônia (America/Porto_Velho)' },
  { valor: 'America/Boa_Vista', rotulo: 'Roraima (America/Boa_Vista)' },
  { valor: 'America/Rio_Branco', rotulo: 'Acre (America/Rio_Branco)' },
  { valor: 'UTC', rotulo: 'UTC' },
]

const MSG_RAZAO = 'A razão social deve ter entre 3 e 150 caracteres.'

// Espelha a validação do servidor, sem substituí-la (RNF-020, RNF-FE-20).
export const empresaSchema = z.object({
  razaoSocial: z
    .string()
    .trim()
    .min(1, 'Informe a razão social.')
    .min(3, MSG_RAZAO)
    .max(150, MSG_RAZAO),
  nomeFantasia: z
    .string()
    .trim()
    .max(150, 'O nome fantasia deve ter no máximo 150 caracteres.'),
  cnpj: z
    .string()
    .min(1, 'Informe o CNPJ.')
    .refine((valor) => validarCnpj(somenteDigitos(valor)), 'CNPJ inválido.'),
  email: z
    .string()
    .trim()
    .max(160, 'O e-mail deve ter no máximo 160 caracteres.')
    .refine(
      (valor) => valor === '' || emailValido(valor),
      'Informe um e-mail válido.',
    ),
  telefone: z
    .string()
    .refine(
      (valor) => valor === '' || validarTelefone(somenteDigitos(valor)),
      'Informe um telefone válido com DDD.',
    ),
  fusoHorario: z.enum(FUSOS_HORARIOS.map((fuso) => fuso.valor)),
})

export const VALORES_INICIAIS = {
  razaoSocial: '',
  nomeFantasia: '',
  cnpj: '',
  email: '',
  telefone: '',
  fusoHorario: 'America/Sao_Paulo',
}

/** Empresa da API -> valores do formulário (com máscara). */
export const deEmpresa = (empresa) => ({
  razaoSocial: empresa.razaoSocial,
  nomeFantasia: empresa.nomeFantasia ?? '',
  cnpj: mascaraCnpj(empresa.cnpj),
  email: empresa.email ?? '',
  telefone: mascaraTelefone(empresa.telefone ?? ''),
  fusoHorario: empresa.fusoHorario,
})

/** Valores do formulário -> corpo da API: CNPJ e telefone só com dígitos (RNF-FE-28). */
export const paraPayload = (valores) => ({
  razaoSocial: valores.razaoSocial.trim(),
  nomeFantasia: valores.nomeFantasia.trim() || null,
  cnpj: somenteDigitos(valores.cnpj),
  email: valores.email.trim() || null,
  telefone: somenteDigitos(valores.telefone) || null,
  fusoHorario: valores.fusoHorario,
  moeda: 'BRL', // nesta fase somente BRL (RN-05 do RF-BE-002)
})
