import { defineConfig } from 'vite'
import solid from 'vite-plugin-solid'
import tailwindcss from '@tailwindcss/vite'
import nexy from "./__nexy__/vite"

export default defineConfig({
  
  plugins: [
    nexy(), 
    solid(),
    tailwindcss(),
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