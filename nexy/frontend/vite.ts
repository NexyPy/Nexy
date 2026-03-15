import {  createLogger,type Logger, type Plugin } from 'vite'
import path from 'node:path'

const nexybase = (mode:string) =>  mode === 'production' ? '/__nexy__/client/' : '/';
const nexyalias = [
  { find: /^@nexy\//, replacement: path.resolve(process.cwd(), '__nexy__/src') + '/' },
  { find: /^@\//, replacement: path.resolve(process.cwd(), 'src') + '/' }
]
const nexybuild = {
      manifest: true,
      outDir: '__nexy__/client',
      rollupOptions: {
        input: {
          main: path.resolve(process.cwd(), '__nexy__/main.ts')
        }
      }
    }

const c = {
  reset: '\x1b[0m',
  magenta: '\x1b[35m',
  dim: '\x1b[2m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[35m',
}

// --- Plugin personnalisé pour Nexy ---
const nexy = (): Plugin => {
  return {
    name: 'nexy-hmr-sync',
    // ghOn demande à Vite de surveiller aussi les fichiers Python et Nexy
    configureServer(server) {
      // On écoute les modifications de fichiers via le watcher de Vite
      server.watcher.add([
        path.resolve(process.cwd(), '**/*.py'),
        path.resolve(process.cwd(), '**/*.nexy'),
        path.resolve(process.cwd(), '**/*.mdx')
      ])

      server.watcher.on('change', (file) => {
        if (file.endsWith('.py') || file.endsWith('.nexy') || file.endsWith('.mdx')) {
          // On envoie un signal de rechargement complet au navigateur
          server.ws.send({
            type: 'full-reload',
            path: '*',
          })
        }

        // let relPath = file.replace(path.resolve(__dirname), '').replaceAll('\\', '/')
        // if (relPath.startsWith('/')) relPath = relPath.slice(1)
        // console.log(`[hmr] ${relPath}`)
      })
    }
  }
}



  const nexyLogger = (): Logger => {
    const logger = createLogger()
    const prefix = `${c.reset}${c.yellow}${c.dim}VITE${c.reset} »`
    return {
      ...logger,
      info: (msg) => {
        const silentMessages = ['Local', 'Network', 'ready in', 'press', 'watching',]
        if (silentMessages.some(m => msg.includes(m))) {return}
        else if (msg.includes('hmr')) {
          msg = msg.replace('hmr ', '')          
        }
        console.info(`${prefix} ${msg.replace("/","")}`)
      },
      warn: (msg) => console.warn(`${prefix} ${c.yellow}⚠ ${msg}${c.reset}`),
      error: (msg) => console.error(`${prefix} ${c.red}✘ ${msg}${c.reset}`),
      
    }
  }

  export {
    nexybuild,
    nexyLogger,
    nexybase,
    nexyalias,
    nexy
  }