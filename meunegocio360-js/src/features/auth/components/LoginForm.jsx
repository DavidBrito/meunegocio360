import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import Alert from 'react-bootstrap/Alert'
import Button from 'react-bootstrap/Button'
import Form from 'react-bootstrap/Form'
import Spinner from 'react-bootstrap/Spinner'
import { useForm } from 'react-hook-form'
import { useLocation } from 'react-router'
import { useCountdown } from '../hooks/useCountdown.js'
import { useLogin } from '../hooks/useLogin.js'
import { loginSchema } from '../schemas.js'

const CAMPOS = ['email', 'senha']

function textoBloqueio(segundos) {
  const minutos = Math.max(1, Math.ceil(segundos / 60))
  return `Muitas tentativas. Tente novamente em ${minutos} ${minutos === 1 ? 'minuto' : 'minutos'}.`
}

export default function LoginForm() {
  const location = useLocation()
  const login = useLogin()
  const bloqueio = useCountdown()
  const [alerta, setAlerta] = useState(
    location.state?.expirou ? 'expirou' : null,
  )

  const {
    register,
    handleSubmit,
    setError,
    setFocus,
    resetField,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', senha: '' },
    mode: 'onSubmit', // valida no envio...
    reValidateMode: 'onChange', // ...e, depois do primeiro envio, a cada alteração
  })

  const enviar = handleSubmit(async (valores) => {
    setAlerta(null)
    try {
      await login.mutateAsync(valores)
      // Sucesso: o AuthProvider passa a `autenticado` e <PublicOnly> redireciona à rota de origem.
    } catch (erro) {
      // Decisão por `code`, nunca pelo texto da mensagem (RNF-FE-14).
      if (erro.code === 'INVALID_CREDENTIALS') {
        setAlerta('credenciais')
        resetField('senha')
        setFocus('senha')
      } else if (erro.code === 'ACCOUNT_TEMPORARILY_LOCKED') {
        setAlerta('bloqueio')
        bloqueio.iniciar(erro.retryAfter ?? 60)
      } else if (erro.code === 'VALIDATION_ERROR') {
        const doServidor = erro.errors.filter((e) => CAMPOS.includes(e.field))
        doServidor.forEach((e) =>
          setError(e.field, { type: 'server', message: e.message }),
        )
        if (doServidor.length > 0) setFocus(doServidor[0].field)
        else setAlerta('rede')
      } else {
        setAlerta('rede')
      }
    }
  })

  const bloqueado = bloqueio.restante > 0
  const enviando = login.isPending

  return (
    <Form noValidate onSubmit={enviar} aria-label="Entrar">
      {alerta === 'expirou' && (
        <Alert variant="warning">Sua sessão expirou. Entre novamente.</Alert>
      )}
      {alerta === 'credenciais' && (
        <Alert variant="danger">E-mail ou senha inválidos.</Alert>
      )}
      {alerta === 'bloqueio' && bloqueado && (
        <Alert variant="danger">{textoBloqueio(bloqueio.restante)}</Alert>
      )}
      {alerta === 'rede' && (
        <Alert variant="danger">
          <p className="mb-2">
            Não foi possível entrar agora. Verifique sua conexão e tente
            novamente.
          </p>
          <Button
            variant="outline-dark"
            size="sm"
            onClick={enviar}
            disabled={enviando}
          >
            Tentar novamente
          </Button>
        </Alert>
      )}

      <Form.Group className="mb-3" controlId="login-email">
        <Form.Label>E-mail</Form.Label>
        <Form.Control
          type="email"
          autoComplete="username"
          isInvalid={Boolean(errors.email)}
          aria-invalid={errors.email ? 'true' : 'false'}
          aria-describedby={errors.email ? 'login-email-erro' : undefined}
          {...register('email')}
        />
        <Form.Control.Feedback type="invalid" id="login-email-erro">
          {errors.email?.message}
        </Form.Control.Feedback>
      </Form.Group>

      <Form.Group className="mb-4" controlId="login-senha">
        <Form.Label>Senha</Form.Label>
        <Form.Control
          type="password"
          autoComplete="current-password"
          isInvalid={Boolean(errors.senha)}
          aria-invalid={errors.senha ? 'true' : 'false'}
          aria-describedby={errors.senha ? 'login-senha-erro' : undefined}
          {...register('senha')}
        />
        <Form.Control.Feedback type="invalid" id="login-senha-erro">
          {errors.senha?.message}
        </Form.Control.Feedback>
      </Form.Group>

      <Button
        type="submit"
        variant="primary"
        className="w-100"
        disabled={enviando || bloqueado}
      >
        {enviando ? (
          <>
            <Spinner
              as="span"
              animation="border"
              size="sm"
              aria-hidden="true"
              className="me-2"
            />
            Entrando…
          </>
        ) : (
          'Entrar'
        )}
      </Button>
    </Form>
  )
}
