import { glob } from 'glob'
import fs from 'fs'
import path from 'path'
import { pathToFileURL } from 'node:url'
import { build } from 'vite'
import {
  detectTsxFramework,
  extractPropPaths,
  createJinjaProps,
  restoreJinjaVars,
  isComponent,
  getManifest,
  getAssetTags,
  saveSnippets,
  writeComponent,
  getEntryId,
  c
} from './utils'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function run(): Promise<number> {
  const manifest = getManifest()
  const files = glob.sync('**/*.{tsx,jsx}', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  }).filter(f => detectTsxFramework(path.resolve(process.cwd(), f)) === 'react')

  if (!files.length) return 0

  // --- Batch SSR build: one Vite build for all components ---
  const tempDir = path.resolve(process.cwd(), 'node_modules/.nexy-temp-ssg')
  fs.mkdirSync(tempDir, { recursive: true })
  const timestamp = Date.now()
  const entries: Record<string, string> = {}

  for (let i = 0; i < files.length; i++) {
    entries[`_c${i}`] = path.resolve(process.cwd(), files[i])
  }

  const { default: reactPlugin } = await import('@vitejs/plugin-react')
  await build({
    logLevel: 'silent',
    configFile: false,
    plugins: [reactPlugin()],
    build: {
      ssr: true,
      outDir: tempDir,
      emptyOutDir: true,
      rollupOptions: {
        input: entries,
        output: {
          entryFileNames: `[name].mjs`,
          format: 'esm'
        },
        external: ['react', 'react-dom', 'react/jsx-runtime', 'react/jsx-dev-runtime']
      }
    }
  })

  const modules = new Map<string, Record<string, any>>()
  for (let i = 0; i < files.length; i++) {
    const outFile = path.join(tempDir, `_c${i}.mjs`)
    if (fs.existsSync(outFile)) {
      const mod = await import(`${pathToFileURL(outFile).href}?t=${timestamp}`)
      modules.set(files[i], mod)
    }
  }

  fs.rmSync(tempDir, { recursive: true, force: true })
  // --- End batch SSR build ---

  const snippets: Record<string, string> = {}

  for (const file of files) {
    const relativeDir = path.dirname(file)
    const ext = path.extname(file)
    const fileName = path.basename(file, ext)

    const propPaths = extractPropPaths(path.resolve(process.cwd(), file))
    const jinjaProps = createJinjaProps(propPaths)

    const mod = modules.get(file)
    if (!mod) {
      console.error(`${c.red} Failed to load ${file}${c.reset}`)
      continue
    }

    for (const [exportName, Component] of Object.entries(mod)) {
      if (!isComponent(exportName, Component, fileName)) continue

      const entryId = getEntryId(fileName, exportName, 'react')

      let html = ''
      try {
        const { renderToString } = await import('react-dom/server')
        const { createElement } = await import('react')
        html = renderToString(createElement(Component as any, jinjaProps))
        html = restoreJinjaVars(html, propPaths)
      } catch (e) {
        console.error(`${c.red} Failed to render ${entryId}${c.reset} in server`)
        continue
      }

      const { css } = getAssetTags(manifest, fileName)
      writeComponent(relativeDir, entryId, `${css}${html}`, snippets)
    }
  }

  saveSnippets(snippets)
  return Object.keys(snippets).length
}