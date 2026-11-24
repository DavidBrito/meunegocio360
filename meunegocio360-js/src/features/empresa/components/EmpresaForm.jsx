import { zodResolver } from '@hookform/resolvers/zod'
import { useRef, useState } from 'react'
import Button from 'react-bootstrap/Button'
import Form from 'react-bootstrap/Form'
import Spinner from 'react-bootstrap/Spinner'
import { Controller, useForm } from 'react-hook-form'
import { mascaraCnpj, mascaraTelefone } from '../../../shared/lib/documentos.js'
import ErrorAlert from '../../../shared/ui/ErrorAlert.jsx'
import MaskedInput from '../../../shared/ui/MaskedInput.jsx'
import { useEmpresa } from '../hooks/useEmpresa.js'
import { useSalvarEmpresa } from '../hooks/useEmpresaMutations.js'
import {
  deEmpresa,
  empresaSchema,
  FUSOS_HORARIOS,
  paraPayload,
  VALORES_INICIAIS,
} from '../schemas.js'

const CAMPOS = [
  'razaoSocial',
  'nomeFantasia',
  'cnpj',
  'email',
  'telefone',
  'fusoHorario',
]

const MENSAGENS = {
  ativa:
    'Já existe uma empresa ativa. Inative-a antes de cadastrar ou reativar outra.',
  permissao: 'Você não tem permissão para alterar os dados da empresa.',
  conflito:
    'Os dados da empresa foram alterados por outra pessoa. Recarregue para ver a versão atual; o que você digitou continua aqui até você escolher.',
  rede: 'Não foi possível salvar agora. Verifique sua conexão e tente novamente. O que você digitou foi mantido.',
  generico:
    'Não foi possível salvar a empresa. Revise os campos e tente novamente.',
}

/**
 * Formulário de cadastro (sem `empresa`) e de edição (com `empresa`). Comportamentos por
 * `code` da API (RNF-FE-14/29): 409 no campo CNPJ, alertas, conflito de versão com
 * "Recarregar dados" e erros 400 ligados aos campos.
 */
export default function EmpresaForm({
  empresa = null,
  aoEnviar,
  aoSalvar,
  aoCancelar,
}) {
  const { recarregar } = useEmpresa()
  const salvar = useSalvarEmpresa(empresa)
  const [erro, setErro] = useState(null)
  const enviando = useRef(false) // impede envio duplicado antes do próximo render

  const {
    control,
    register,
    handleSubmit,
    setError,
    setFocus,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(empresaSchema),
    defaultValues: empresa ? deEmpresa(empresa) : VALORES_INICIAIS,
    mode: 'onSubmit',
    reValidateMode: 'onChange',
  })

  const enviar = handleSubmit(async (valores) => {
    setErro(null)
    aoEnviar?.()
    try {
      // Atenção: `aoSalvar?.(await ...)` NÃO avalia o argumento quando `aoSalvar` é undefined.
      const salva = await salvar.mutateAsync(paraPayload(valores))
      aoSalvar?.(salva)
    } catch (falha) {
      tratarFalha(falha)
    }
  })

  // Segundo clique antes do primeiro terminar não gera nova requisição (RF-FE-002).
  async function aoSubmeter(evento) {
    evento.preventDefault()
    if (enviando.current) return
    enviando.current = true
    try {
      await enviar(evento)
    } finally {
      enviando.current = false
    }
  }

  function tratarFalha(falha) {
    if (falha.code === 'COMPANY_CNPJ_DUPLICATE') {
      setError('cnpj', {
        type: 'server',
        message: 'Já existe uma empresa cadastrada com este CNPJ.',
      })
      setFocus('cnpj')
    } else if (falha.code === 'COMPANY_ALREADY_ACTIVE') {
      setErro('ativa')
    } else if (falha.code === 'VERSION_CONFLICT') {
      setErro('conflito')
    } else if (falha.code === 'ACCESS_DENIED') {
      setErro('permissao')
    } else if (falha.code === 'VALIDATION_ERROR') {
      const doServidor = falha.errors.filter((item) =>
        CAMPOS.includes(item.field),
      )
      doServidor.forEach((item) =>
        setError(item.field, { type: 'server', message: item.message }),
      )
      if (doServidor.length > 0) setFocus(doServidor[0].field)
      else setErro('generico')
    } else {
      setErro('rede')
    }
  }

  async function recarregarDados() {
    const { data } = await recarregar()
    if (data) reset(deEmpresa(data))
    setErro(null)
  }

  const acao = {
    conflito: { rotulo: 'Recarregar dados', aoClicar: recarregarDados },
    rede: {
      rotulo: 'Tentar novamente',
      aoClicar: aoSubmeter,
      desabilitado: salvar.isPending,
    },
  }[erro]

  const campoInvalido = (nome) => ({
    isInvalid: Boolean(errors[nome]),
    'aria-invalid': errors[nome] ? 'true' : 'false',
    'aria-describedby': errors[nome] ? `empresa-${nome}-erro` : undefined,
  })
  const feedback = (nome) => (
    <Form.Control.Feedback type="invalid" id={`empresa-${nome}-erro`}>
      {errors[nome]?.message}
    </Form.Control.Feedback>
  )

  return (
    <Form
      noValidate
      onSubmit={aoSubmeter}
      aria-label={empresa ? 'Editar empresa' : 'Cadastrar empresa'}
    >
      {erro && (
        <ErrorAlert acao={acao} className="mb-3">
          {MENSAGENS[erro]}
        </ErrorAlert>
      )}
      <p className="text-body-secondary">
        Campos marcados com * são obrigatórios.
      </p>

      <Form.Group className="mb-3" controlId="empresa-razaoSocial">
        <Form.Label>
          Razão social <span aria-hidden="true">*</span>
        </Form.Label>
        <Form.Control
          type="text"
          autoComplete="organization"
          aria-required="true"
          {...campoInvalido('razaoSocial')}
          {...register('razaoSocial')}
        />
        {feedback('razaoSocial')}
      </Form.Group>

      <Form.Group className="mb-3" controlId="empresa-nomeFantasia">
        <Form.Label>Nome fantasia</Form.Label>
        <Form.Control
          type="text"
          {...campoInvalido('nomeFantasia')}
          {...register('nomeFantasia')}
        />
        {feedback('nomeFantasia')}
      </Form.Group>

      <Form.Group className="mb-3" controlId="empresa-cnpj">
        <Form.Label>
          CNPJ <span aria-hidden="true">*</span>
        </Form.Label>
        <Controller
          name="cnpj"
          control={control}
          render={({ field: { ref, value, onChange, onBlur, name } }) => (
            <MaskedInput
              mascara={mascaraCnpj}
              inputRef={ref}
              value={value}
              onChange={onChange}
              onBlur={onBlur}
              name={name}
              type="text"
              inputMode="numeric"
              autoComplete="off"
              placeholder="00.000.000/0000-00"
              aria-required="true"
              {...campoInvalido('cnpj')}
            />
          )}
        />
        {feedback('cnpj')}
      </Form.Group>

      <Form.Group className="mb-3" controlId="empresa-email">
        <Form.Label>E-mail</Form.Label>
        <Form.Control
          type="email"
          autoComplete="email"
          {...campoInvalido('email')}
          {...register('email')}
        />
        {feedback('email')}
      </Form.Group>

      <Form.Group className="mb-3" controlId="empresa-telefone">
        <Form.Label>Telefone</Form.Label>
        <Controller
          name="telefone"
          control={control}
          render={({ field: { ref, value, onChange, onBlur, name } }) => (
            <MaskedInput
              mascara={mascaraTelefone}
              inputRef={ref}
              value={value}
              onChange={onChange}
              onBlur={onBlur}
              name={name}
              type="tel"
              autoComplete="tel"
              placeholder="(00) 00000-0000"
              {...campoInvalido('telefone')}
            />
          )}
        />
        {feedback('telefone')}
      </Form.Group>

      <Form.Group className="mb-3" controlId="empresa-fusoHorario">
        <Form.Label>Fuso horário</Form.Label>
        <Form.Select
          {...campoInvalido('fusoHorario')}
          {...register('fusoHorario')}
        >
          {FUSOS_HORARIOS.map((fuso) => (
            <option key={fuso.valor} value={fuso.valor}>
              {fuso.rotulo}
            </option>
          ))}
        </Form.Select>
        {feedback('fusoHorario')}
      </Form.Group>

      <Form.Group className="mb-4" controlId="empresa-moeda">
        <Form.Label>Moeda</Form.Label>
        <Form.Select disabled value="BRL" onChange={() => {}}>
          <option value="BRL">BRL — Real brasileiro</option>
        </Form.Select>
        <Form.Text>Nesta fase somente o real é aceito.</Form.Text>
      </Form.Group>

      <div className="d-flex flex-wrap gap-2">
        <Button type="submit" variant="primary" disabled={salvar.isPending}>
          {salvar.isPending ? (
            <>
              <Spinner
                as="span"
                animation="border"
                size="sm"
                aria-hidden="true"
                className="me-2"
              />
              Salvando…
            </>
          ) : (
            'Salvar'
          )}
        </Button>
        {aoCancelar && (
          <Button
            type="button"
            variant="outline-dark"
            onClick={aoCancelar}
            disabled={salvar.isPending}
          >
            Cancelar
          </Button>
        )}
      </div>
    </Form>
  )
}
