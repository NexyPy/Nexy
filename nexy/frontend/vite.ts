import { createLogger, type Logger, type Plugin} from 'vite'
import path from 'node:path'
import { execSync } from 'child_process'
import { createRequire } from 'module'
import { pathToFileURL } from 'url'

const c = {
  reset:  '\x1b[0m',
  dim:    '\x1b[2m',
  yellow: '\x1b[33m',
  red:    '\x1b[31m',
}

function getTsxPath(): string {
  const require = createRequire(import.meta.url)
  try {
    const resolved = require.resolve('tsx/esm')
    return pathToFileURL(resolved).href
  } catch {
    throw new Error(' "tsx" is required. Run: pnpm add -D tsx')
  }
}

let nexySSGDone = false
let isSSRBuild = false

function nexyPlugin(): Plugin {
  return {
    name: 'nexy',

    // --- Configuration Automatique ---
    // Cette partie injecte tes réglages directement dans Vite
    config( { mode }) {
      return {
        logLevel: 'info',
        base: mode === 'production' ? '/__nexy__/client/' : '/',
        
        resolve: {
          alias: [
            { find: /^@nexy\//, replacement: path.resolve(process.cwd(), '__nexy__/src') + '/' },
            { find: /^@\//, replacement: path.resolve(process.cwd(), 'src') + '/' }
          ]
        },

        server: {
          strictPort: true,
          cors: { 
            origin: true, 
            methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'] 
          },
          watch: {
            // Empêche les boucles infinies de rebuild lors du SSG
            ignored: [
              '**/node_modules/**', 
              '**/__nexy__/client/**', 
              '**/__nexy__/**/*.{html,py}', 
              '**/.git/**'
            ]
          }
        },

        build: {
          manifest: true,
          outDir: '__nexy__/client',
          rollupOptions: {
            input: {
              main: path.resolve(process.cwd(), '__nexy__/main.ts')
            }
          }
        }
      }
    },

    configResolved(config) {
      isSSRBuild = !!config.build?.ssr
    },

    // --- HMR pour les fichiers non-JS (Python, Nexy, MDX) ---
    configureServer(server) {
      server.watcher.add([
        path.resolve(process.cwd(), '**/*.py'),
        path.resolve(process.cwd(), '**/*.nexy'),
        path.resolve(process.cwd(), '**/*.mdx')
      ])

      server.watcher.on('change', (file) => {
        if (file.endsWith('.py') || file.endsWith('.nexy') || file.endsWith('.mdx')) {
          server.ws.send({ type: 'full-reload', path: '*' })
        }
      })
    },

    // --- Génération des Entrées (Client side) ---
    buildStart() {
      if (isSSRBuild) return
      nexySSGDone = false
      const isDev = process.env.NODE_ENV === 'development'
      if (!isDev) {
        const tsxPath = getTsxPath()
        console.log(`${c.dim}Preparing Vite ...${c.reset}`)
        execSync(`node --import "${tsxPath}" __nexy__/scripts/entries.ts`, {
          stdio: 'inherit',
          cwd: process.cwd()
        })
      }
    },

    // --- Static Site Generation (SSG) ---
    closeBundle() {
      if (isSSRBuild || nexySSGDone) return
      nexySSGDone = true

      const tsxPath = getTsxPath()
      // console.log(`${c.dim}Running Static Site Generation...${c.reset}`)
      execSync(`node --import "${tsxPath}" __nexy__/scripts/ssg.ts`, {
        stdio: 'inherit',
        cwd: process.cwd()
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
      const silentMessages = ['Local', 'Network', 'ready in', 'press', 'watching']
      if (silentMessages.some(m => msg.includes(m))) return
      console.info(`${prefix} ${msg.replace("/", "")}`)
    },
    warn: (msg) => console.warn(`${prefix} ${c.yellow}⚠ ${msg}${c.reset}`),
    error: (msg) => console.error(`${prefix} ${c.red}✘ ${msg}${c.reset}`),
  }
}

const nexy = Object.assign(nexyPlugin, {
  log: nexyLogger
})

export default nexy
