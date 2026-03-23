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
async function loadModule(file: string): Promise<Record<string, any>> {
  const tempDir = path.resolve(process.cwd(), 'node_modules/.nexy-temp')
  fs.mkdirSync(tempDir, { recursive: true })

  const timestamp = Date.now()
  const ext = path.extname(file)
  const fileName = path.basename(file, ext)
  const absoluteFile = path.resolve(process.cwd(), file)
  const outFile = path.join(tempDir, `${fileName}-${timestamp}.mjs`)

  const { default: reactPlugin } = await import('@vitejs/plugin-react')

  await build({
    logLevel: 'silent',
    configFile: false,
    plugins: [reactPlugin()],
    build: {
      ssr: true,
      outDir: path.dirname(outFile),
      emptyOutDir: false,
      rollupOptions: {
        input: { [fileName]: absoluteFile },
        output: {
          entryFileNames: `${fileName}-${timestamp}.mjs`,
          format: 'esm'
        },
        external: ['react', 'react-dom', 'react/jsx-runtime', 'react/jsx-dev-runtime']
      }
    }
  })

  if (!fs.existsSync(outFile)) {
    throw new Error(` Vite failed to produce output for ${fileName}`)
  }

  const mod = await import(`${pathToFileURL(outFile).href}?t=${timestamp}`)
  fs.rmSync(outFile, { force: true })
  return mod
}

export async function run(): Promise<number> {
  const manifest = getManifest()
  const files = glob.sync('**/*.{tsx,jsx}', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  }).filter(f => detectTsxFramework(path.resolve(process.cwd(), f)) === 'react')

  if (!files.length) return 0

  const snippets: Record<string, string> = {}

  for (const file of files) {
    const relativeDir = path.dirname(file)
    const ext = path.extname(file)
    const fileName = path.basename(file, ext)

    const propPaths = extractPropPaths(path.resolve(process.cwd(), file))
    const jinjaProps = createJinjaProps(propPaths)

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let mod: Record<string, any>
    try {
      mod = await loadModule(file)
    } catch (err) {
      console.error(`${c.red} Failed to load ${file}:${c.reset}`, err)
      continue
    }

    for (const [exportName, Component] of Object.entries(mod)) {
      if (!isComponent(exportName, Component, fileName)) continue

      const entryId = getEntryId(fileName, exportName, 'react')

      let html = ''
      try {
        const { renderToString } = await import('react-dom/server')
        const { createElement } = await import('react')
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        html = renderToString(createElement(Component as any, jinjaProps))
        html = restoreJinjaVars(html, propPaths)
      } catch (e) {
        console.error(`${c.red} Failed to render ${entryId}:${c.reset}`, e)
        continue
      }

      const { css } = getAssetTags(manifest, fileName)
      writeComponent(relativeDir, entryId, `${css}${html}`, snippets)
    }
  }

  fs.rmSync(path.resolve(process.cwd(), 'node_modules/.nexy-temp'), { recursive: true, force: true })
  saveSnippets(snippets)
  return Object.keys(snippets).length
}