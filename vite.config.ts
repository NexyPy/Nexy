import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'node:fs'
import path from 'node:path'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => {
  const serverPortFile = path.resolve('__nexy__/server.port')
  let serverPort = Number(process.env.__NEXY_SERVER_PORT) || 3000
  try {
    if (fs.existsSync(serverPortFile)) {
      const txt = fs.readFileSync(serverPortFile, 'utf8').trim()
      const n = Number(txt)
      if (!Number.isNaN(n) && n > 0) serverPort = n
    }
  } catch {}
  const origin = `http://localhost:${serverPort}`
  return {
    base: mode === 'production' ? '/__nexy__/client/' : '/',
    plugins: [react(), tailwindcss(),],
    build: {
      manifest: true,
      outDir: '__nexy__/client',
      rollupOptions: {
        input: {
          main: '__nexy__/main.ts'
        }
      }
    },
    resolve: {
      alias: {
        '@': '/src/components'
      }
    },
    envPrefix: ['NEXY_'],
    server: {
      port: 5173,
      strictPort: true,
      origin,
      cors: { origin },
      watch: {
        // Ignore heavy dirs and ALL __nexy__ artifacts; keep HMR on src/**
        ignored: [
          '**/node_modules/**',
          '**/.git/**',
          '**/.venv/**',
          '**/venv/**',
          '**/__pycache__/**',
          '**/__nexy__/**'
        ]
      }
    },
    customLogger: {
      info: (msg: string) => console.log(msg),
      warn: (msg: string) => console.warn(msg),
      error: (msg: string) => console.error(msg),
      clearScreen: () => console.clear(),
      hasErrorLogged: () => false,
      warnOnce: () => {},
      hasWarned: false
    },
    optimizeDeps: {}
  }
})
