import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [react()],
    server: {
      // Em desenvolvimento o navegador chama /api na mesma origem e o Vite repassa ao backend
      // (RNF-103): o cookie de refresh continua first-party, com SameSite=Strict.
      proxy: {
        '/api': { target: env.API_PROXY_TARGET || 'http://localhost:8080' },
      },
    },
    css: {
      preprocessorOptions: {
        // O Bootstrap 5.3 ainda usa @import e funcoes globais do Sass.
        scss: {
          quietDeps: true,
          silenceDeprecations: [
            'import',
            'global-builtin',
            'color-functions',
            'if-function',
          ],
        },
      },
    },
  }
})
