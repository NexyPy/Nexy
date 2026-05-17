import { glob } from 'glob'
import fs from 'fs'
import path from 'path'
import { pathToFileURL } from 'node:url'
import { build } from 'vite'
import {
  getManifest,
  getAssetTags,
  saveSnippets,
  writeComponent,
  getEntryId,
  type SSGResult,
  c
} from './utils'

async function loadModule(file: string): Promise<Record<string, any>> {
  const tempDir = path.resolve(process.cwd(), 'node_modules/.nexy-temp')
  fs.mkdirSync(tempDir, { recursive: true })

  const timestamp = Date.now()
  const fileName = path.basename(file, '.vue')
  const outFile = path.join(tempDir, `${fileName}-${timestamp}.mjs`)

  const absoluteComponentPath = path.resolve(process.cwd(), file).replace(/\\/g, '/')
  const entryFile = path.join(tempDir, `${fileName}-entry-${timestamp}.js`)

  fs.writeFileSync(entryFile, `import Component from '${absoluteComponentPath}'; export default Component;`)

  const { default: vuePlugin } = await import('@vitejs/plugin-vue')

  await build({
    logLevel: 'warn',
    configFile: false,
    plugins: [vuePlugin()],
    build: {
      ssr: true,
      outDir: path.dirname(outFile),
      emptyOutDir: false,
      rollupOptions: {
        input: { [fileName]: entryFile },
        output: {
          entryFileNames: `${fileName}-${timestamp}.mjs`,
          format: 'esm'
        },
        external: ['vue', '@vue/server-renderer']
      }
    }
  })

  fs.rmSync(entryFile, { force: true })

  if (!fs.existsSync(outFile)) {
    throw new Error(` Vite failed to produce output for ${fileName}`)
  }

  const mod = await import(`${pathToFileURL(outFile).href}?t=${timestamp}`)
  fs.rmSync(outFile, { force: true })
  return mod
}

export async function run(): Promise<SSGResult> {
  const result: SSGResult = { entries: [] }
  const manifest = getManifest()
  const files = glob.sync('**/*.vue', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  })

  if (!files.length) return result

  const snippets: Record<string, string> = {}

  for (const file of files) {
    const relativeDir = path.dirname(file)
    const fileName = path.basename(file, '.vue')

    let mod: Record<string, any>
    try {
      mod = await loadModule(file)
    } catch (err) {
      result.entries.push({ file, component: '*', status: 'not_supported' })
      continue
    }

    const Component = mod.default
    if (!Component) {
      result.entries.push({ file, component: '*', status: 'not_supported' })
      continue
    }

    try {
      const { renderToString } = await import('@vue/server-renderer')
      const { createSSRApp } = await import('vue')
      const html = await renderToString(createSSRApp(Component))
      const entryId = getEntryId(fileName, 'Default', 'vue')
      const { css } = getAssetTags(manifest, fileName)
      writeComponent(relativeDir, entryId, `${css}${html}`, snippets)
      result.entries.push({ file, component: 'Default', status: 'success' })
    } catch (e) {
      result.entries.push({ file, component: 'Default', status: 'failed' })
    }
  }

  fs.rmSync(path.resolve(process.cwd(), 'node_modules/.nexy-temp'), { recursive: true, force: true })
  saveSnippets(snippets)
  return result
}
