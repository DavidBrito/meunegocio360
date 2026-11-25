import { Link } from 'react-router'

export default function AcessoNegadoPage() {
  return (
    <>
      <title>Acesso negado — MeuNegócio360</title>
      <h1 className="h2">Acesso negado</h1>
      <p>Seu perfil não tem permissão para acessar esta página.</p>
      <Link to="/">Ir para o início</Link>
    </>
  )
}
