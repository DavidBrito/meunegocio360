import { Suspense } from 'react'
import { Outlet } from 'react-router'
import PageLoading from '../shared/ui/PageLoading.jsx'

/** Layout raiz: páginas carregadas sob demanda com fallback acessível (RNF-FE-05). */
export default function RootLayout() {
  return (
    <Suspense fallback={<PageLoading />}>
      <Outlet />
    </Suspense>
  )
}
