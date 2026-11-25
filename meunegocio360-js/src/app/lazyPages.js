import { lazy } from 'react'

// Páginas carregadas sob demanda (RNF-FE-05); as de feature vêm do `index.js` de cada feature.
export const HomePage = lazy(() => import('./pages/HomePage.jsx'))
export const NotFoundPage = lazy(() => import('./pages/NotFoundPage.jsx'))
