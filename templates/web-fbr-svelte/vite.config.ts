import { defineConfig} from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'
import { nexy, nexyLogger, nexyalias, nexybase, nexybuild } from "./__nexy__/vite"

export default defineConfig(({ mode }) => {
  return {
    base: nexybase(mode),
    plugins: [
      svelte(),
      tailwindcss(),
      nexy()
    ],
    optimizeDeps: {
      esbuildOptions: undefined
    },
    customLogger: nexyLogger(),
    logLevel: 'info',
    server: {
      strictPort: true,
      cors: { 
        origin: true,
        methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
      },
      watch: {
        ignored: ['**/node_modules/**', '**/__nexy__/client/**', '**/.git/**']
      }
    },
    build: nexybuild,
    resolve: {
      alias: [...nexyalias]
    }
  }
})
