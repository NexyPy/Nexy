import { defineConfig } from 'vite'
import preact from '@preact/preset-vite'
import tailwindcss from '@tailwindcss/vite'
import nexy from "./__nexy__/vite"

export default defineConfig({
  
  plugins: [
    nexy(), 
    preact(),
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