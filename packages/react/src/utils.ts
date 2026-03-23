/* eslint-disable @typescript-eslint/no-explicit-any */
import fs from 'fs'
import path from 'path'
import { glob } from 'glob'
import ts from 'typescript'

export type Framework = 'react' | 'preact' | 'solid' | 'vue' | 'svelte'

export const c = {
  reset:  '\x1b[0m',
  dim:    '\x1b[2m',
  yellow: '\x1b[33m',
  red:    '\x1b[31m',
  green:  '\x1b[32m',
}

export const FRAMEWORK_PACKAGES: Record<Framework, string> = {
  react:  'react',
  preact: 'preact',
  solid:  'solid-js',
  vue:    'vue',
  svelte: 'svelte',
}

export function getProjectFrameworks(): Set<Framework> {
  const frameworks = new Set<Framework>()
  const files = glob.sync('**/*.{tsx,jsx,vue,svelte}', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  })

  for (const file of files) {
    if (file.endsWith('.vue')) {
      frameworks.add('vue')
    } else if (file.endsWith('.svelte')) {
      frameworks.add('svelte')
    } else if (file.endsWith('.tsx') || file.endsWith('.jsx')) {
      const content = fs.readFileSync(path.resolve(process.cwd(), file), 'utf-8')
      if (content.includes("from 'solid-js'") || content.includes('from "solid-js"')) {
        frameworks.add('solid')
      } else if (content.includes("from 'preact'") || content.includes('from "preact"')) {
        frameworks.add('preact')
      } else {
        frameworks.add('react')
      }
    }
  }

  return frameworks
}

export function checkFrameworks(usedFrameworks: Set<Framework>): Set<Framework> {
  const installed = new Set<Framework>()
  for (const framework of usedFrameworks) {
    const pkgPath = path.resolve(process.cwd(), 'node_modules', FRAMEWORK_PACKAGES[framework])
    if (fs.existsSync(pkgPath)) {
      installed.add(framework)
    } else {
      console.warn(
        `${c.yellow} "${framework}" is used but not installed.` +
        ` Run: pnpm add ${FRAMEWORK_PACKAGES[framework]}${c.reset}`
      )
    }
  }
  return installed
}

export function isFrameworkInstalled(framework: Framework): boolean {
  return fs.existsSync(
    path.resolve(process.cwd(), 'node_modules', FRAMEWORK_PACKAGES[framework])
  )
}

export function detectTsxFramework(filePath: string): 'react' | 'preact' | 'solid' | null {
  if (!filePath.endsWith('.tsx') && !filePath.endsWith('.jsx')) return null
  const content = fs.readFileSync(filePath, 'utf-8')

  if (content.includes("from 'solid-js'") || content.includes('from "solid-js"')) return 'solid'
  if (content.includes("from 'preact'")   || content.includes('from "preact"'))   return 'preact'

  // Vérifier aussi le dossier parent — si le fichier est dans un template preact/solid
  const normalizedPath = filePath.replace(/\\/g, '/')
  if (normalizedPath.includes('web-fbr-preact') || normalizedPath.includes('/preact/')) return 'preact'
  if (normalizedPath.includes('web-fbr-solid')  || normalizedPath.includes('/solid/'))  return 'solid'

  return 'react'
}

export function extractPropPaths(filePath: string): string[] {
  const program = ts.createProgram([filePath], { jsx: ts.JsxEmit.React, strict: true })
  const checker = program.getTypeChecker()
  const source = program.getSourceFile(filePath)
  if (!source) return []

  const paths: string[] = []

  function isPrimitive(type: ts.Type): boolean {
    const flags = type.getFlags()
    return !!(
      flags & ts.TypeFlags.String ||
      flags & ts.TypeFlags.Number ||
      flags & ts.TypeFlags.Boolean ||
      flags & ts.TypeFlags.StringLiteral ||
      flags & ts.TypeFlags.NumberLiteral ||
      flags & ts.TypeFlags.BooleanLiteral ||
      flags & ts.TypeFlags.Undefined ||
      flags & ts.TypeFlags.Null ||
      (type.isUnion() && type.types.every(t => isPrimitive(t)))
    )
  }

  function isFunction(type: ts.Type): boolean {
    return type.getCallSignatures().length > 0
  }

  function walk(type: ts.Type, prefix: string, depth = 0) {
    if (depth > 5) return
    if (isPrimitive(type)) {
      if (prefix) paths.push(prefix)
      return
    }
    if (isFunction(type)) return
    const props = checker.getPropertiesOfType(type)
    if (props.length === 0) {
      if (prefix) paths.push(prefix)
      return
    }
    for (const prop of props) {
      const propType = checker.getTypeOfSymbol(prop)
      const propPath = prefix ? `${prefix}.${prop.name}` : prop.name
      if (isFunction(propType)) continue
      if (isPrimitive(propType)) {
        paths.push(propPath)
      } else {
        walk(propType, propPath, depth + 1)
      }
    }
  }

  const tryExtract = (fn: ts.SignatureDeclaration) => {
    const sig = checker.getSignatureFromDeclaration(fn)
    if (!sig) return
    const param = sig.parameters[0]
    if (!param) return
    const type = checker.getTypeOfSymbolAtLocation(param, fn)
    walk(type, '')
  }

  ts.forEachChild(source, node => {
    if (ts.isFunctionDeclaration(node)) tryExtract(node)
    if (ts.isVariableStatement(node)) {
      ts.forEachChild(node.declarationList, decl => {
        if (!ts.isVariableDeclaration(decl) || !decl.initializer) return
        const init = decl.initializer
        if (ts.isArrowFunction(init) || ts.isFunctionExpression(init)) tryExtract(init)
      })
    }
  })

  return [...new Set(paths)]
}

export const PLACEHOLDER_PREFIX = 'NEXY'

export const createJinjaProps = (propPaths: string[]): Record<string, any> => {
  const result: Record<string, any> = {}
  for (const propPath of propPaths) {
    const parts = propPath.split('.')
    let current = result
    for (let i = 0; i < parts.length - 1; i++) {
      current[parts[i]] ??= {}
      current = current[parts[i]]
    }
    const last = parts[parts.length - 1]
    current[last] = `${PLACEHOLDER_PREFIX}${propPath.replace(/\./g, 'DOT')}`
  }
  return result
}

export const restoreJinjaVars = (html: string, propPaths: string[]): string => {
  let result = html
  const sorted = [...propPaths].sort((a, b) => b.length - a.length)
  for (const propPath of sorted) {
    const placeholder = `${PLACEHOLDER_PREFIX}${propPath.replace(/\./g, 'DOT')}`
    result = result.split(placeholder).join(`{{ ${propPath} }}`)
  }
  return result
}

export const isComponent = (exportName: string, Component: any, fileName: string): boolean => {
  if (typeof Component !== 'function') return false
  if (Component.prototype?.isReactComponent) return true
  const source = Component.toString().trim()
  if (source.startsWith('class') && !source.includes('isReactComponent')) return false
  const name = exportName === 'default' ? (Component.name || fileName) : exportName
  return /^[A-Z]/.test(name)
}

export function getManifest(): Record<string, any> {
  const manifestPath = path.resolve(process.cwd(), '__nexy__/client/.vite/manifest.json')
  if (!fs.existsSync(manifestPath)) {
    console.error(`${c.red} Manifest not found. Run vite build first.${c.reset}`)
    process.exit(1)
  }
  return JSON.parse(fs.readFileSync(manifestPath, 'utf-8'))
}

export function getAssetTags(manifest: Record<string, any>, fileName: string): { js: string, css: string } {
  const entry = Object.values(manifest).find((e: any) =>
    e.file.includes(fileName) && !e.file.endsWith('.css')
  ) as any

  // const js = entry?.file ? `<script type="module" src="/${entry.file}"></script>` : ''
  const js =""
  const css = entry?.css?.map((csf: string) => `<link rel="stylesheet" href="/${csf}">`).join('') || ''

  return { js, css }
}

export function saveSnippets(newSnippets: Record<string, string>) {
  const snippetsPath = path.resolve(process.cwd(), '__nexy__/client/snippets.json')
  const existing = fs.existsSync(snippetsPath)
    ? JSON.parse(fs.readFileSync(snippetsPath, 'utf-8'))
    : {}

  fs.mkdirSync(path.resolve(process.cwd(), '__nexy__/client/static'), { recursive: true })
  fs.writeFileSync(snippetsPath, JSON.stringify({ ...existing, ...newSnippets }, null, 2))
}

export function writeComponent(
  relativeDir: string,
  entryId: string,
  finalContent: string,
  snippets: Record<string, string>
) {
  const outputDir = path.join(process.cwd(), '__nexy__/client/static', relativeDir)
  fs.mkdirSync(outputDir, { recursive: true })
  fs.writeFileSync(path.join(outputDir, `${entryId}.html`), finalContent)

  const snippetKey = path.join(relativeDir, `${entryId}.html`).replace(/\\/g, '/')
  snippets[snippetKey] = finalContent

  console.log(`${c.dim} __nexy__/client/static/${snippetKey}${c.reset}`)
}


export function getEntryId(
  fileName: string,
  exportName: string,
  framework: Framework
): string {
  // Vue et Svelte → filename.vue.html / filename.svelte.html
  if (framework === 'vue') return `${fileName}.vue`
  if (framework === 'svelte') return `${fileName}.svelte`

  // React, Preact, Solid → filename.Default.html / filename.MyComp.html
  return `${fileName}.${exportName === 'default' ? 'Default' : exportName}`
}

export function getTempDir(): string {
  const tempDir = path.resolve(process.cwd(), '__nexy__', '.temp');
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true });
  }
  return tempDir;
}