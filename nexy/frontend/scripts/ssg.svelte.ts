/* eslint-disable @typescript-eslint/no-explicit-any */
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
  c
} from './utils'

async function loadModule(file: string): Promise<Record<string, any>> {
  const tempDir = path.resolve(process.cwd(), 'node_modules/.nexy-temp')
  fs.mkdirSync(tempDir, { recursive: true })

  const fileName = path.basename(file, '.svelte')
  const timestamp = Date.now()
  const outFile = path.join(tempDir, `${fileName}-${timestamp}.mjs`)

  const absoluteFile = path.resolve(process.cwd(), file)

  const { svelte: sveltePlugin } = await import('@sveltejs/vite-plugin-svelte')
  await build({
    logLevel: 'silent',
    configFile: false,
    // ✅ root = dossier du fichier pour éviter "cannot be external"
    root: path.dirname(absoluteFile),
    plugins: [sveltePlugin()],
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
        external: ['svelte', 'svelte/server', 'svelte/internal']
      }
    }
  })

  const generated = fs.readdirSync(path.dirname(outFile))
    .find(f => f === `${fileName}-${timestamp}.mjs`)

  if (!generated) throw new Error(`[nexy] Vite failed to produce output for ${fileName}`)

  const mod = await import(`${pathToFileURL(outFile).href}?t=${timestamp}`)
  fs.rmSync(outFile, { force: true })
  return mod
}

export async function run(): Promise<number> {
  const manifest = getManifest()
  const files = glob.sync('**/*.svelte', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  })

  if (!files.length) return 0

  const snippets: Record<string, string> = {}

  for (const file of files) {
    const relativeDir = path.dirname(file)
    const fileName = path.basename(file, '.svelte')

    let mod: Record<string, any>
    try {
      mod = await loadModule(file)
    } catch (err) {
      console.error(`${c.red}[nexy] Failed to load ${file}:${c.reset}`, err)
      continue
    }

    const Component = mod.default
    if (!Component) continue

    let html = ''
    try {
      const svelte = await import('svelte/server')
      const { createRawSnippet } = await import('svelte')

      const emptySnippet = createRawSnippet(() => ({
        render: () => '',
        setup: () => { }
      }))

      html = svelte.render(Component, {
        props: { children: emptySnippet }
      }).html
    } catch (e) {
      console.error(`${c.red}[nexy] Failed to render ${fileName}:${c.reset}`, e)
      continue
    }

    const entryId = getEntryId(fileName, "Default", 'svelte')
    const { css } = getAssetTags(manifest, fileName)
    writeComponent(relativeDir, entryId, `${css}${html}`, snippets)
  }

  fs.rmSync(path.resolve(process.cwd(), 'node_modules/.nexy-temp'), { recursive: true, force: true })
  saveSnippets(snippets)
  return Object.keys(snippets).length
}