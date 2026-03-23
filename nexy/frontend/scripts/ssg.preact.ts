import { glob } from 'glob'
import fs from 'fs'
import path from 'path'
import { pathToFileURL } from 'node:url'
import esbuild from 'esbuild'
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
  c,

} from './utils'

async function loadModule(file: string): Promise<Record<string, any>> {
  const tempDir = path.resolve(process.cwd(), 'node_modules/.nexy-temp')
  fs.mkdirSync(tempDir, { recursive: true })

  const ext = path.extname(file)
  const fileName = path.basename(file, ext)
  const outFile = path.join(tempDir, `${fileName}-${Date.now()}.mjs`)

  await esbuild.build({
    entryPoints: [path.resolve(file)],
    outfile: outFile,
    bundle: true,
    format: 'esm',
    platform: 'node',
    jsx: 'automatic',
    jsxImportSource: 'preact',
    external: ['preact', 'preact/jsx-runtime'],
    logLevel: 'silent'
  })

  const mod = await import(pathToFileURL(outFile).href)
  fs.rmSync(outFile, { force: true })
  return mod
}

export async function run(): Promise<number> {
  const manifest = getManifest()
  const files = glob.sync('**/*.{tsx,jsx}', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  }).filter(f => detectTsxFramework(path.resolve(process.cwd(), f)) === 'preact')

  if (!files.length) return 0

  const snippets: Record<string, string> = {}

  for (const file of files) {
    const relativeDir = path.dirname(file)
    const ext = path.extname(file)
    const fileName = path.basename(file, ext)

    const propPaths = extractPropPaths(path.resolve(process.cwd(), file))
    const jinjaProps = createJinjaProps(propPaths)

    let mod: Record<string, any>
    try {
      mod = await loadModule(file)
    } catch (err) {
      console.error(`${c.red} Failed to load ${file}:${c.reset}`, err)
      continue
    }

    for (const [exportName, Component] of Object.entries(mod)) {
      if (!isComponent(exportName, Component, fileName)) continue

      const entryId = getEntryId(fileName, exportName, 'preact')

      let html = ''
      try {
        const { renderToString } = await import('preact-render-to-string')
        const { h } = await import('preact')
        html = renderToString(h(Component as any, jinjaProps))
        html = restoreJinjaVars(html, propPaths)
      } catch (e) {
        console.error(`${c.red} Failed to render ${entryId}:${c.reset}`, e)
        continue
      }

      const {  css } = getAssetTags(manifest, fileName)
      writeComponent(relativeDir, entryId, `${css}${html}`, snippets)
    }
  }

  fs.rmSync(path.resolve(process.cwd(), 'node_modules/.nexy-temp'), { recursive: true, force: true })
  saveSnippets(snippets)
  return Object.keys(snippets).length
}