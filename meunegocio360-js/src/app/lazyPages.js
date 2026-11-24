import { lazy } from 'react'

// Páginas carregadas sob demanda (RNF-FE-05); a de login é exportada por features/auth.
export const HomePage = lazy(() => import('./pages/HomePage.jsx'))
export const NotFoundPage = lazy(() => import('./pages/NotFoundPage.jsx'))
