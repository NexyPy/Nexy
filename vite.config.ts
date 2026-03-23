


import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import preact from '@preact/preset-vite'
import solid from 'vite-plugin-solid'
import nexy from "./__nexy__/vite"

export default defineConfig({
  plugins: [
    nexy(), 
    tailwindcss(),
    react(),
    vue(),
    svelte(),
    preact(),
    solid()
  ],
  customLogger: nexy.log(),
  build: {
    rollupOptions: {
      // Pour ignorer des fichiers lors du build final
      external: [
        // Exemple : si vous voulez que certains fichiers ne soient pas packagés
        /.*\/templates\/*/,
      ],
  }},
  server :{
     watch : {
        ignored: ['**/node_modules/**', '**/__nexy__/client/**', '**/.git/**','**/templates/**']
     }
  }
})
