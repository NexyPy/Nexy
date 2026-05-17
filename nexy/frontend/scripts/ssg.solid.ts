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
  type SSGResult,
  c
} from './utils'

export async function run(): Promise<SSGResult> {
  const result: SSGResult = { entries: [] }
  const manifest = getManifest()
  const files = glob.sync('**/*.{tsx,jsx}', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  }).filter(f => detectTsxFramework(path.resolve(process.cwd(), f)) === 'solid')

  if (!files.length) return result

  const tempDir = path.resolve(process.cwd(), 'node_modules/.nexy-temp-ssg')
  fs.mkdirSync(tempDir, { recursive: true })
  const timestamp = Date.now()
  const entries: Record<string, string> = {}

  for (let i = 0; i < files.length; i++) {
    entries[`_c${i}`] = path.resolve(process.cwd(), files[i])
  }

  const { default: viteSolidPlugin } = await import('vite-plugin-solid')
  await build({
    logLevel: 'silent',
    configFile: false,
    plugins: [
      viteSolidPlugin({
        ssr: true
      })
    ],
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
        external: ['solid-js', 'solid-js/web', 'solid-js/store']
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

  const snippets: Record<string, string> = {}

  for (const file of files) {
    const relativeDir = path.dirname(file)
    const ext = path.extname(file)
    const fileName = path.basename(file, ext)

    const propPaths = extractPropPaths(path.resolve(process.cwd(), file))
    const jinjaProps = createJinjaProps(propPaths)

    const mod = modules.get(file)
    if (!mod) {
      result.entries.push({ file, component: '*', status: 'not_supported' })
      continue
    }

    let hasComponent = false
    for (const [exportName, Component] of Object.entries(mod)) {
      if (!isComponent(exportName, Component, fileName)) continue
      hasComponent = true

      const entryId = getEntryId(fileName, exportName, 'solid')

      try {
        const { renderToString } = await import('solid-js/web')
        const html = renderToString(() => (Component as any)(jinjaProps))
        const out = restoreJinjaVars(html, propPaths)
        const { css } = getAssetTags(manifest, fileName)
        writeComponent(relativeDir, entryId, `${css}${out}`, snippets)
        result.entries.push({ file, component: exportName === 'default' ? 'Default' : exportName, status: 'success' })
      } catch (e) {
        result.entries.push({ file, component: exportName === 'default' ? 'Default' : exportName, status: 'failed' })
      }
    }
    if (!hasComponent) {
      result.entries.push({ file, component: '*', status: 'not_supported' })
    }
  }

  saveSnippets(snippets)
  return result
}
