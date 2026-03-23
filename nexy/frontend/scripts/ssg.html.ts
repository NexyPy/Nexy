import { glob } from 'glob'
import path from 'path'
import {
  getManifest,
  getAssetTags,
  saveSnippets,
  writeComponent,
  
} from './utils'

// Compile tsx en HTML pur via esbuild uniquement — pas de renderToString
export async function run(): Promise<number> {
  const manifest = getManifest()
  const files = glob.sync('**/*.{tsx,jsx}', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  })

  if (!files.length) return 0

  const snippets: Record<string, string> = {}

  for (const file of files) {
    const relativeDir = path.dirname(file)
    const ext = path.extname(file)
    const fileName = path.basename(file, ext)

    const {  css } = getAssetTags(manifest, fileName)

    // Pas de renderToString — juste le script + css
    const entryId = `${fileName}.Default`
    const finalContent = `${css}<div id="${entryId}-root"></div>`

    writeComponent(relativeDir, entryId, finalContent, snippets)
  }

  saveSnippets(snippets)
  return Object.keys(snippets).length
}