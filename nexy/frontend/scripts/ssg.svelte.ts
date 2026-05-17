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

  const fileName = path.basename(file, '.svelte')
  const timestamp = Date.now()
  const outFile = path.join(tempDir, `${fileName}-${timestamp}.mjs`)

  const absoluteFile = path.resolve(process.cwd(), file)

  const { svelte: sveltePlugin } = await import('@sveltejs/vite-plugin-svelte')
  await build({
    logLevel: 'silent',
    configFile: false,
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

  if (!generated) throw new Error(` Vite failed to produce output for ${fileName}`)

  const mod = await import(`${pathToFileURL(outFile).href}?t=${timestamp}`)
  fs.rmSync(outFile, { force: true })
  return mod
}

export async function run(): Promise<SSGResult> {
  const result: SSGResult = { entries: [] }
  const manifest = getManifest()
  const files = glob.sync('**/*.svelte', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  })

  if (!files.length) return result

  const snippets: Record<string, string> = {}

  for (const file of files) {
    const relativeDir = path.dirname(file)
    const fileName = path.basename(file, '.svelte')

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
      const svelte = await import('svelte/server')
      const { createRawSnippet } = await import('svelte')
      const emptySnippet = createRawSnippet(() => ({
        render: () => '',
        setup: () => { }
      }))

      const { html } = svelte.render(Component, {
        props: { children: emptySnippet }
      })

      const entryId = getEntryId(fileName, "Default", 'svelte')
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
