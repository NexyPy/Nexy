import { glob } from 'glob'
import { getProjectFrameworks, checkFrameworks, c } from './utils'
import { type SSGResult, writeReport } from './utils'
import { JSDOM } from 'jsdom'

async function run() {
  const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>')

  Object.defineProperty(global, 'window', { value: dom.window, writable: true })
  Object.defineProperty(global, 'document', { value: dom.window.document, writable: true })

  Object.defineProperty(dom.window, 'matchMedia', {
    writable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    })
  })

  global.localStorage = {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {},
    clear: () => {},
    length: 0,
    key: () => null
  } as any
  const usedFrameworks = getProjectFrameworks()
  const installedFrameworks = checkFrameworks(usedFrameworks)
  const results: SSGResult[] = []

  const hasTsx = glob.sync('**/*.{tsx,jsx}', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  }).length > 0

  if (hasTsx) {
    if (installedFrameworks.has('react')) {
      const { run } = await import('./ssg.react')
      results.push(await run())
    }
    if (installedFrameworks.has('preact')) {
      const { run } = await import('./ssg.preact')
      results.push(await run())
    }
    if (installedFrameworks.has('solid')) {
      const { run } = await import('./ssg.solid')
      results.push(await run())
    }
    if (
      !installedFrameworks.has('react') &&
      !installedFrameworks.has('preact') &&
      !installedFrameworks.has('solid')
    ) {
      const { run } = await import('./ssg.html')
      results.push(await run())
    }
  }

  if (usedFrameworks.has('vue')) {
    if (installedFrameworks.has('vue')) {
      const { run } = await import('./ssg.vue')
      results.push(await run())
    } else {
      console.warn(`${c.yellow} *.vue files found but vue is not installed. Run: pnpm add vue${c.reset}`)
    }
  }

  if (usedFrameworks.has('svelte')) {
    if (installedFrameworks.has('svelte')) {
      const { run } = await import('./ssg.svelte')
      results.push(await run())
    } else {
      console.warn(`${c.yellow} *.svelte files found but svelte is not installed. Run: pnpm add svelte${c.reset}`)
    }
  }

  writeReport(results)

  const all = results.flatMap(r => r.entries)
  const success = all.filter(e => e.status === 'success').length
  const failed = all.filter(e => e.status === 'failed').length
  const notSupported = all.filter(e => e.status === 'not_supported').length
  if (all.length) {
    console.log(`  ssg       » [reset][dim]${success} ok, ${failed} failed, ${notSupported} skipped[/dim] [green]✓[/green]`)
  }
}

run().then(() => process.exit(0)).catch(err => {
  console.error(' SSG failed:', err)
  process.exit(1)
})
