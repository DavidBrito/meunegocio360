import { createBrowserRouter } from 'react-router'
import {
  LoginPage,
  PublicOnly,
  RequireAuth,
  RequireRole,
} from '../features/auth'
import {
  EmpresaCadastroPage,
  EmpresaPage,
  EmpresaProvider,
  RequireEmpresa,
} from '../features/empresa'
import { PERFIS } from '../shared/lib/perfis.js'
import AppLayout from './AppLayout.jsx'
import { HomePage, NotFoundPage } from './lazyPages.js'
import RootLayout from './RootLayout.jsx'

/*
 * Rotas protegidas: RequireAuth (sessão) -> EmpresaProvider (empresa resolvida) -> AppLayout.
 * /empresa e /empresa/cadastro ficam fora de RequireEmpresa (precisam funcionar sem empresa).
 */
export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      {
        element: <PublicOnly />,
        children: [{ path: '/login', element: <LoginPage /> }],
      },
      {
        element: <RequireAuth />,
        children: [
          {
            element: (
              <EmpresaProvider>
                <AppLayout />
              </EmpresaProvider>
            ),
            children: [
              { path: '/empresa', element: <EmpresaPage /> },
              {
                element: <RequireRole perfis={[PERFIS.ADMIN]} />,
                children: [
                  {
                    path: '/empresa/cadastro',
                    element: <EmpresaCadastroPage />,
                  },
                ],
              },
              {
                element: <RequireEmpresa />,
                children: [{ path: '/', element: <HomePage /> }],
              },
            ],
          },
        ],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
