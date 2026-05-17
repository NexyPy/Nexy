import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import nexy from "./__nexy__/vite"

export default defineConfig({
  
  plugins: [
    nexy(), 
    tailwindcss(),
  ],
  customLogger: nexy.log(),
  build :{
    rollupOptions: {
    output: {
      format: 'esm',
    },
    external: [], 
  }
  }
})