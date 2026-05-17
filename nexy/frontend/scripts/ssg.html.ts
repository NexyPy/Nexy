import { glob } from 'glob'
import path from 'path'
import {
  getManifest,
  getAssetTags,
  saveSnippets,
  writeComponent,
  type SSGResult,
} from './utils'

export async function run(): Promise<SSGResult> {
  const result: SSGResult = { entries: [] }
  const manifest = getManifest()
  const files = glob.sync('**/*.{tsx,jsx}', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  })

  if (!files.length) return result

  const snippets: Record<string, string> = {}

  for (const file of files) {
    const relativeDir = path.dirname(file)
    const ext = path.extname(file)
    const fileName = path.basename(file, ext)

    const { css } = getAssetTags(manifest, fileName)

    const entryId = `${fileName}.Default`
    const finalContent = `${css}<div id="${entryId}-root"></div>`

    writeComponent(relativeDir, entryId, finalContent, snippets)
    result.entries.push({ file, component: 'Default', status: 'success' })
  }

  saveSnippets(snippets)
  return result
}
