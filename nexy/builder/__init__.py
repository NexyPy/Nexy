from nexy.builder.discovery import Discovery
from nexy.compiler import Compiler
from nexy.core.config import Config
from pathlib import Path


class Builder:
    def __init__(self):
        self.discovery = Discovery()
        self.compiler = Compiler()
        self.config = Config()

        exclude_dirs = getattr(self.config, "excludeDirs", [])
        for name in exclude_dirs:
            self.discovery.add_excluded_dir(name)

    def build(self) -> None:
        files = self.discovery.scan(self.config.PROJECT_ROOT)
        for file in files:
            input_path = file.as_posix()
            self.compiler.compile(input=input_path)
        self._generate_vite_entry()
    
    def _generate_vite_entry(self) -> None:
        ff_list = getattr(self.config, "useFF", None) or []
        frameworks: set[str] = {getattr(ff, "name", "").lower() for ff in ff_list if getattr(ff, "name", None)}
        dest_dir = Path("__nexy__")
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "main.ts"
        parts: list[str] = []
        parts.append("type CompMod = { default: unknown }")
        parts.append("type Importer = () => Promise<CompMod>")
        parts.append("type Importers = Record<string, Importer>")
        parts.append("type NexyProps = Record<string, unknown>")
        parts.append("const importers: Importers = {")
        parts.append("  ...import.meta.glob('/src/**/*.{tsx,jsx,ts,js,vue,svelte}', { eager: false }) as Record<string, Importer>,")
        parts.append("}")
        parts.append("function normalizePath(p: string): string { return p && !p.startsWith('/') ? `/${p}` : p }")
        if "react" in frameworks:
            parts.append("async function __nexy_setup_preamble(){")
            parts.append("  if (!(import.meta && import.meta.env && import.meta.env.DEV)) return")
            parts.append("  const mod = await import('/@react-refresh')")
            parts.append("  const RefreshRuntime = (mod as { default: any }).default")
            parts.append("  RefreshRuntime.injectIntoGlobalHook(window as any)")
            parts.append("  ;(window as any).$RefreshReg$ = () => {}")
            parts.append("  ;(window as any).$RefreshSig$ = () => (type: unknown) => type")
            parts.append("  ;(window as any).__vite_plugin_react_preamble_installed__ = true")
            parts.append("}")
        else:
            parts.append("async function __nexy_setup_preamble(){}")
        if "react" in frameworks:
            parts.append("async function mountReact(el: HTMLElement, path: string, props: NexyProps, symbol: string): Promise<void> {")
            parts.append("  const loader = importers[path]")
            parts.append("  if (!loader) throw new Error(`Component not found: ${path}`)")
            parts.append("  const mod = await loader()")
            parts.append("  const anyMod = mod as Record<string, unknown> & CompMod")
            parts.append("  const Comp = (anyMod.default ?? (symbol && anyMod[symbol])) as unknown")
            parts.append("  const React = (await import('react')) as typeof import('react')")
            parts.append("  const RDC = (await import('react-dom/client')) as typeof import('react-dom/client')")
            parts.append("  const root = RDC.createRoot(el)")
            parts.append("  root.render(React.createElement(Comp as never, props as never))")
            parts.append("}")
        if "vue" in frameworks:
            parts.append("async function mountVue(el: HTMLElement, path: string, props: NexyProps): Promise<void> {")
            parts.append("  const loader = importers[path]")
            parts.append("  if (!loader) throw new Error(`Component not found: ${path}`)")
            parts.append("  const mod = await loader()")
            parts.append("  const Comp = (mod as CompMod).default as unknown")
            parts.append("  const vue = await import(/* @vite-ignore */ 'vue').catch(()=>{ throw new Error('Vue not installed') })")
            parts.append("  const app = (vue as typeof import('vue')).createApp({ render: () => (vue as typeof import('vue')).h(Comp as never, props as never) })")
            parts.append("  app.mount(el)")
            parts.append("}")
        if "svelte" in frameworks:
            parts.append("async function mountSvelte(el: HTMLElement, path: string, props: NexyProps): Promise<void> {")
            parts.append("  const loader = importers[path]")
            parts.append("  if (!loader) throw new Error(`Component not found: ${path}`)")
            parts.append("  const mod = await loader()")
            parts.append("  const Comp = (mod as CompMod).default as unknown")
            parts.append("  new (Comp as new (args: { target: HTMLElement; props: NexyProps }) => unknown)({ target: el, props })")
            parts.append("}")
        if "preact" in frameworks:
            parts.append("async function mountPreact(el: HTMLElement, path: string, props: NexyProps): Promise<void> {")
            parts.append("  const loader = importers[path]")
            parts.append("  if (!loader) throw new Error(`Component not found: ${path}`)")
            parts.append("  const mod = await loader()")
            parts.append("  const Comp = (mod as CompMod).default as unknown")
            parts.append("  const preact = await import(/* @vite-ignore */ 'preact').catch(()=>{ throw new Error('Preact not installed') })")
            parts.append("  ;(preact as typeof import('preact')).render((preact as typeof import('preact')).h(Comp as never, props as never), el)")
            parts.append("}")
        parts.append("async function mountOne(el: Element): Promise<void> {")
        parts.append("  if(!(el instanceof HTMLElement)) return")
        parts.append("  if(el.dataset.nexyMounted==='1') return")
        parts.append("  el.dataset.nexyMounted='1'")
        parts.append("  const fw=(el.dataset.nexyFw||'').toLowerCase()")
        parts.append("  const rawPath=el.dataset.nexyPath||''")
        parts.append("  const symbol = el.getAttribute('data-nexy-symbol') || ''")
        parts.append("  const propsStr=el.dataset.nexyProps||'{}'")
        parts.append("  let props: NexyProps = {}")
        parts.append("  try{ props=JSON.parse(propsStr) as NexyProps }catch{}")
        parts.append("  let path=normalizePath(rawPath)")
        parts.append("  if(!importers[path]){ const alt = path.startsWith('/')?path.slice(1):path; if(importers[alt]) path=alt; else { return } }")
        if "react" in frameworks:
            parts.append("  if(fw==='react') return mountReact(el, path, props, symbol)")
        if "vue" in frameworks:
            parts.append("  if(fw==='vue') return mountVue(el, path, props)")
        if "svelte" in frameworks:
            parts.append("  if(fw==='svelte') return mountSvelte(el, path, props)")
        if "preact" in frameworks:
            parts.append("  if(fw==='preact') return mountPreact(el, path, props)")
        parts.append("}")
        parts.append("async function init(): Promise<void> {")
        parts.append("  await __nexy_setup_preamble();")
        parts.append("  document.querySelectorAll('[data-nexy-fw]').forEach((el)=>{ void mountOne(el) })")
        parts.append("}")
        parts.append("if(document.readyState==='loading'){ document.addEventListener('DOMContentLoaded', ()=>{ void init() }) } else { void init() }")
        dest.write_text("\n".join(parts), encoding="utf-8")


__all__ = ["Builder"]
