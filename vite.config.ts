import { defineConfig, createLogger,type Logger, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'node:fs'
import path from 'node:path'

const c = {
  reset: '\x1b[0m',
  magenta: '\x1b[35m',
  dim: '\x1b[2m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
}

// --- Plugin personnalisé pour Nexy ---
const nexy = (): Plugin => {
  return {
    name: 'nexy-hmr-sync',
    // ghOn demande à Vite de surveiller aussi les fichiers Python et Nexy
    configureServer(server) {
      // On écoute les modifications de fichiers via le watcher de Vite
      server.watcher.add([
        path.resolve(__dirname, '**/*.py'),
        path.resolve(__dirname, '**/*.nexy'),
        path.resolve(__dirname, '**/*.mdx')
      ])

      server.watcher.on('change', (file) => {
        if (file.endsWith('.py') || file.endsWith('.nexy') || file.endsWith('.mdx')) {
          // On envoie un signal de rechargement complet au navigateur
          server.ws.send({
            type: 'full-reload',
            path: '*'
          })
        }

        // let relPath = file.replace(path.resolve(__dirname), '').replaceAll('\\', '/')
        // if (relPath.startsWith('/')) relPath = relPath.slice(1)
        // console.log(`[hmr] ${relPath}`)
      })
    }
  }
}

export default defineConfig(({ mode }) => {
  const serverPortFile = path.resolve('__nexy__/server.port')
  let serverPort = 3000
  
  try {
    if (fs.existsSync(serverPortFile)) {
      const txt = fs.readFileSync(serverPortFile, 'utf8').trim()
      serverPort = Number(txt) || 3000
    }
  } catch {}

  const origin = `http://localhost:${serverPort}`

  const nexyLogger = (): Logger => {
    const logger = createLogger()
    const prefix = `[hmr]`
    return {
      ...logger,
      info: (msg, options) => {
        const silentMessages = ['Local', 'Network', 'ready in', 'press', 'watching',]
        if (silentMessages.some(m => msg.includes(m))) {return}
        else if (msg.includes('hmr')) {
          msg = msg.replace('hmr ', '')          
        }
        console.info(`${prefix} ${msg.replace("/","")}`)
      },
      warn: (msg, options) => console.warn(`${prefix} ${c.yellow}⚠ ${msg}${c.reset}`),
      error: (msg, options) => console.error(`${prefix} ${c.red}✘ ${msg}${c.reset}`),
      
    }
  }

  return {
    base: mode === 'production' ? '/__nexy__/client/' : '/',
    plugins: [
      react(),
      nexy() // On active notre plugin ici
    ],
    
    customLogger: nexyLogger(),
    logLevel: 'info',

    server: {
      port: 5173,
      strictPort: true,
      origin,
      cors: { origin },
      watch: {
        // ATTENTION : On retire les extensions .py, .nexy, .mdx des ignorés
        // pour que le plugin puisse les voir, mais on ignore toujours __nexy__
        ignored: ['**/node_modules/**', '**/__nexy__/**', '**/.git/**']
      }
    },

    build: {
      manifest: true,
      outDir: '__nexy__/client',
      rollupOptions: {
        input: {
          main: path.resolve(__dirname, '__nexy__/main.ts')
        }
      }
    },

    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src/components')
      }
    }
  }
})