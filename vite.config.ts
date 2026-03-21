import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import vue from '@vitejs/plugin-vue'
import { nexy, nexyLogger, nexyalias, nexybase, nexybuild } from "./__nexy__/vite"
// import svelte from '@vitejs/plugin-svelte' // Commented out because module not found
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => {



  return {
    base: nexybase(mode),
    plugins: [
      react(),
      tailwindcss(),
      vue(),
      // svelte(),
      nexy() 
    ],

    customLogger: nexyLogger(),
    logLevel: 'info',

    server: {
      strictPort: true,
      origin: '*',
      cors: true,
      watch: {
        // On ignore uniquement la sortie de build, pas les sources __nexy__/src
        ignored: ['**/node_modules/**', '**/__nexy__/client/**', '**/.git/**', "**/__nexy__/src/**"]
      }
    },

    build: nexybuild,

    resolve: {
      alias: [...nexyalias]
    }
  }
})
