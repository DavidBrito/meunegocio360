import { z } from 'zod'

// Espelha a validação do servidor, sem substituí-la (RNF-020, RNF-FE-20). Mensagens do RF-FE-001.
export const loginSchema = z.object({
  email: z
    .string()
    .trim()
    .min(1, 'Informe seu e-mail.')
    .max(160, 'O e-mail deve ter no máximo 160 caracteres.')
    .pipe(z.email('Informe um e-mail válido.')),
  senha: z
    .string()
    .min(1, 'Informe sua senha.')
    .min(8, 'A senha deve ter entre 8 e 72 caracteres.')
    .max(72, 'A senha deve ter entre 8 e 72 caracteres.'),
})
