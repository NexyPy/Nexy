import { defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { nexy, nexyLogger, nexyalias, nexybase, nexybuild } from "./__nexy__/vite"

export default defineConfig(({ mode }) => {
  return {
    base: nexybase(mode),
    plugins: [
      vue(),
      tailwindcss(),
      nexy()
    ],
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
