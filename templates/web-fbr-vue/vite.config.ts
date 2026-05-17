import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import nexy from "./__nexy__/vite"

export default defineConfig({
  
  plugins: [
    nexy(), 
    tailwindcss(),
    vue(),
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