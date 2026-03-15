import { defineConfig} from 'vite'
import react from '@vitejs/plugin-react'
import vue from '@vitejs/plugin-vue'
import  {nexy,nexyLogger,nexyalias,nexybase,nexybuild} from "./__nexy__/vite"
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
      nexy() // On active notre plugin ici
    ],
    
    customLogger: nexyLogger(),
    logLevel: 'info',

    server: {
      strictPort: true,
      cors: { 
        origin: true, // Autorise l'origine de la requête entrante
        methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
      },
      watch: {
        // On ignore uniquement la sortie de build, pas les sources __nexy__/src
        ignored: ['**/node_modules/**', '**/__nexy__/client/**', '**/.git/**']
      }
    },

    build: nexybuild,

    resolve: {
      alias: [...nexyalias]
    }
  }
})
