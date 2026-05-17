import { defineConfig } from 'vite'
import {svelte} from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'
import nexy from "./__nexy__/vite"

export default defineConfig({
  
  plugins: [
    nexy(), 
    tailwindcss(),
    svelte(),
  ],
  customLogger: nexy.log(),
  build :{
    rollupOptions: {
    output: {
      format: 'esm',
    },
    // Ne pas mettre 'vue' en external si tu veux que Vite 
    // l'inclue proprement dans le bundle généré
    external: [], 
  }
  }
})