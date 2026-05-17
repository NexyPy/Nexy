import { glob } from 'glob'
import fs from 'fs'
import path from 'path'
import { pathToFileURL } from 'node:url'
import esbuild from 'esbuild'
import {
  type Framework,
  getProjectFrameworks,
  checkFrameworks,
  detectTsxFramework,
  getTempDir,
  c
} from './utils'

async function loadModuleExports(file: string, framework: Framework): Promise<string[]> {
  if (framework === 'vue' || framework === 'svelte') return ['default']

  const tempDir = getTempDir(); // Utilise le nouveau dossier
  const ext = path.extname(file)
  const fileName = path.basename(file, ext)
  const outFile = path.join(tempDir, `${fileName}-${Date.now()}.mjs`)

  await esbuild.build({
    entryPoints: [path.resolve(file)],
    outfile: outFile,
    bundle: true,
    format: 'esm',
    platform: 'node',
    external: ['react', 'preact', 'solid-js'],
    logLevel: 'silent',
  })

  const mod = await import(`${pathToFileURL(outFile).href}?t=${Date.now()}`)
  fs.rmSync(outFile, { force: true })
  return Object.keys(mod)
}

function generateEntryContent(
  framework: Framework,
  entryId: string,
  componentImport: string,
  importPath: string
): string {
  switch (framework) {
    case 'react':
      return `
import { hydrateRoot } from 'react-dom/client'
import React from 'react'
import ${componentImport} from '${importPath}'

const el = document.getElementById('${entryId}-root')
if (el) hydrateRoot(el, React.createElement(Component))
`.trim()

    case 'preact':
      return `
import { hydrate, h } from 'preact'
import ${componentImport} from '${importPath}'

const el = document.getElementById('${entryId}-root')
if (el) hydrate(h(Component, {}), el)
`.trim()

    case 'solid':
      return `
import { hydrate } from 'solid-js/web'
import ${componentImport} from '${importPath}'

const el = document.getElementById('${entryId}-root')
if (el) hydrate(() => Component({}), el)
`.trim()

    case 'vue':
      return `
import { createApp } from 'vue'
import ${componentImport} from '${importPath}'

const el = document.getElementById('${entryId}-root')
if (el) createApp(Component).mount(el)
`.trim()

    case 'svelte':
      return `
import { hydrate } from 'svelte'
import ${componentImport} from '${importPath}'

const el = document.getElementById('${entryId}-root')
if (el) hydrate(Component, { target: el })
`.trim()
  }
}

async function generateEntries() {
  const usedFrameworks = getProjectFrameworks()
  if (usedFrameworks.size === 0) {
    console.warn(`${c.yellow}No components found.${c.reset}`)
    return
  }

  const installedFrameworks = checkFrameworks(usedFrameworks)

  const files = glob.sync('**/*.{tsx,jsx,vue,svelte}', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  })

  const entriesDir = path.resolve(process.cwd(), '__nexy__/client/entries')
  fs.mkdirSync(entriesDir, { recursive: true })

  for (const file of files) {
    const relativePath = path.dirname(file)
    const ext = path.extname(file)
    const fileName = path.basename(file, ext)

    let framework: Framework | null = null
    if (file.endsWith('.vue')) framework = 'vue'
    else if (file.endsWith('.svelte')) framework = 'svelte'
    else framework = detectTsxFramework(path.resolve(process.cwd(), file))

    if (!framework || !installedFrameworks.has(framework)) continue

    let exportNames: string[]
    try {
      exportNames = await loadModuleExports(file, framework)
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);

      // Analyse simplifiée de la cause
      let reason = "internal error";
      if (message.includes("require")) reason = "CommonJS/AMD compatibility ";
      if (message.includes("is not defined")) reason = "missing browser-only global (window/document)";

      console.warn(`[Nexy SSG] Skipping "${file}": Nexy cannot render this component because of ${reason}.`);

      // On peut ajouter une petite note pour le debug si besoin
      // console.debug(`Full error: ${message.split('\n')[0]}`);

      continue;
    }

    for (const exportName of exportNames) {
      const isDefault = exportName === 'default'
      const componentName = isDefault ? 'Default' : exportName
      const entryId = `${fileName}.${componentName}`

      const targetDir = path.join(entriesDir, relativePath)
      fs.mkdirSync(targetDir, { recursive: true })

      const importPath = path.relative(targetDir, path.resolve(process.cwd(), file))
        .replace(/\\/g, '/')
        .replace(/\.(tsx|jsx|vue|svelte)$/, '')

      const componentImport = isDefault ? 'Component' : `{ ${exportName} as Component }`
      const entryExt = framework === 'vue' || framework === 'svelte' ? '.ts' : '.tsx'
      const content = generateEntryContent(framework, entryId, componentImport, importPath)

      fs.writeFileSync(path.join(targetDir, `${entryId}${entryExt}`), content)
    }
  }

  fs.rmSync(path.resolve(process.cwd(), 'node_modules/.nexy-temp'), { recursive: true, force: true })
  console.log('Entries generated successfully')
}

generateEntries().then(() => process.exit(0)).catch(err => {
  console.error('Failed to generate entries:', err)
  process.exit(1)
})