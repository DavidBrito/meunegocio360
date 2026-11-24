import { createBrowserRouter } from 'react-router'
import { LoginPage, PublicOnly, RequireAuth } from '../features/auth'
import { HomePage, NotFoundPage } from './lazyPages.js'
import RootLayout from './RootLayout.jsx'

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
        children: [{ path: '/', element: <HomePage /> }],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
