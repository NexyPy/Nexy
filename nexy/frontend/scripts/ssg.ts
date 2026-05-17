/* eslint-disable @typescript-eslint/no-explicit-any */
import { glob } from 'glob'
import { getProjectFrameworks, checkFrameworks, c } from './utils'
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
  if (usedFrameworks.size === 0) {
    console.warn(`${c.yellow}No components found.${c.reset}`)
    return
  }

  console.log(`Detected: ${[...usedFrameworks].join(', ')}`)
  const installedFrameworks = checkFrameworks(usedFrameworks)

  const hasTsx = glob.sync('**/*.{tsx,jsx}', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  }).length > 0

  if (hasTsx) {
    if (installedFrameworks.has('react')) {
      console.log(`React`)
      const { run } = await import('./ssg.react')
      await run()
    }
    if (installedFrameworks.has('preact')) {
      console.log(`Preact`)
      const { run } = await import('./ssg.preact')
      await run()
    }
    if (installedFrameworks.has('solid')) {
      console.log(`Solid`)
      const { run } = await import('./ssg.solid')
      await run()
    }
    if (
      !installedFrameworks.has('react') &&
      !installedFrameworks.has('preact') &&
      !installedFrameworks.has('solid')
    ) {
      console.log(`${c.yellow} No tsx framework — compiling to plain HTML${c.reset}`)
      const { run } = await import('./ssg.html')
      await run()
    }
  }

  if (usedFrameworks.has('vue')) {
    if (installedFrameworks.has('vue')) {
      console.log(` Vue`)
      const { run } = await import('./ssg.vue')
      await run()
    } else {
      console.warn(`${c.yellow} *.vue files found but vue is not installed. Run: pnpm add vue${c.reset}`)
    }
  }

  if (usedFrameworks.has('svelte')) {
    if (installedFrameworks.has('svelte')) {
      console.log(`Svelte`)
      const { run } = await import('./ssg.svelte')
      await run()
    } else {
      console.warn(`${c.yellow} *.svelte files found but svelte is not installed. Run: pnpm add svelte${c.reset}`)
    }
  }
}

run().then(() => process.exit(0)).catch(err => {
  console.error(' SSG failed:', err)
  process.exit(1)
})