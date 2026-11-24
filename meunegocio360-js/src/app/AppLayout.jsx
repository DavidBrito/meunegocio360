import { Suspense, useState } from 'react'
import Button from 'react-bootstrap/Button'
import Container from 'react-bootstrap/Container'
import Nav from 'react-bootstrap/Nav'
import Navbar from 'react-bootstrap/Navbar'
import { Link, NavLink, Outlet } from 'react-router'
import logoBranca from '../assets/logo-branca.png'
import { useAuth } from '../features/auth'
import { useEmpresa } from '../features/empresa'
import { ROTULOS_PERFIL } from '../shared/lib/perfis.js'
import PageLoading from '../shared/ui/PageLoading.jsx'
import { itensDoPerfil } from './menu.js'

/** Lupa do botão de pesquisa (SVG inline: sem pacote de ícones, RNF-015). */
function IconeLupa() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 16 16"
      fill="currentColor"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001q.044.06.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1 1 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0" />
    </svg>
  )
}

/**
 * Layout das rotas protegidas (RF-FE-002): barra de navegação com o nome da empresa e o menu
 * por perfil. Cores da paleta (RNF-FE 2.1/2.2): fundo Laranja, texto/links/ícones Pretos.
 *
 * Telas grandes (>= lg):  [logo] [Início] [Empresa] ...... [empresa] [usuário · perfil] [Sair]
 * Mobile (< lg):          [☰]  [      logo centralizado      ]  [🔍 desabilitado]
 *                         e o menu abre logo abaixo (empilhado, fecha ao navegar).
 */
export default function AppLayout() {
  const { usuario, sair } = useAuth()
  const { empresa } = useEmpresa()
  const [aberto, setAberto] = useState(false)
  const fechar = () => setAberto(false)
  const nomeEmpresa = empresa
    ? empresa.nomeFantasia || empresa.razaoSocial
    : 'Empresa não cadastrada'

  return (
    <>
      <a
        href="#conteudo"
        className="visually-hidden-focusable position-absolute p-2 bg-body"
      >
        Ir para o conteúdo
      </a>
      <header>
        <Navbar
          expand="lg"
          expanded={aberto}
          onToggle={setAberto}
          className="bg-primary"
        >
          <Container>
            <Navbar.Toggle
              aria-controls="menu-principal"
              aria-label={aberto ? 'Fechar menu' : 'Abrir menu'}
              className="navbar-botao-icone order-1 order-lg-0"
            />
            <Navbar.Brand
              as={Link}
              to="/"
              onClick={fechar}
              className="order-2 order-lg-0 mx-auto mx-lg-0 me-lg-4 py-0"
            >
              <img
                src={logoBranca}
                alt="MeuNegócio360"
                width="198"
                height="40"
                className="d-block img-fluid"
              />
            </Navbar.Brand>
            {/* Placeholder: ainda não existe busca global (decisão do autor, D-080). */}
            <Button
              variant="outline-dark"
              className="navbar-botao-icone order-3 d-lg-none"
              disabled
              aria-label="Pesquisar (em breve)"
            >
              <IconeLupa />
            </Button>
            <Navbar.Collapse id="menu-principal" className="order-4 order-lg-1">
              <Nav as="ul" className="me-lg-auto" aria-label="Menu principal">
                {itensDoPerfil(usuario.perfil).map((item) => (
                  <li key={item.to} className="nav-item">
                    <NavLink
                      to={item.to}
                      end={item.to === '/'}
                      onClick={fechar}
                      className={({ isActive }) =>
                        `nav-link${isActive ? ' active fw-bold text-decoration-underline' : ''}`
                      }
                    >
                      {item.rotulo}
                    </NavLink>
                  </li>
                ))}
              </Nav>
              {/* Separador só no mobile; no desktop o grupo fica na mesma linha */}
              <hr className="d-lg-none my-2" />
              <div className="d-flex flex-column flex-lg-row align-items-lg-center gap-2 gap-lg-3 pb-2 pb-lg-0">
                <span
                  className="navbar-empresa text-truncate fw-semibold"
                  title={nomeEmpresa}
                >
                  {nomeEmpresa}
                </span>
                <div className="lh-sm">
                  <div>{usuario.nome}</div>
                  <div className="small">{ROTULOS_PERFIL[usuario.perfil]}</div>
                </div>
                <Button variant="outline-dark" onClick={sair}>
                  Sair
                </Button>
              </div>
            </Navbar.Collapse>
          </Container>
        </Navbar>
      </header>
      <main id="conteudo" tabIndex={-1}>
        <Container className="py-4">
          <Suspense fallback={<PageLoading compacto />}>
            <Outlet />
          </Suspense>
        </Container>
      </main>
    </>
  )
}
