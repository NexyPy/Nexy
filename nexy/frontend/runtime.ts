type CompMod = { default: unknown }
type Importer = () => Promise<CompMod>
type Importers = Record<string, Importer>
import { __NEXY_KEYS } from '@nexy/keys.auto.ts';
const importers: Importers = import.meta.glob('/src/**/*.{tsx,jsx,ts,js,vue,svelte}', { eager: false }) as Record<string, Importer>
const norm = (p: string) => p && p.startsWith('/') ? p : '/' + p
const w: any = window as any;
w.__nexy_import = (p: string) => {
    let key = p;
    if (!key.startsWith('/')) {
        const mapped = (__NEXY_KEYS as any)[key];
        if (mapped) key = mapped;
    }
    const k1 = norm(key);
    const k2 = k1.startsWith('/') ? k1.slice(1) : k1;
    const imp = (importers as any)[k1] || (importers as any)[k2];
    if (!imp) return Promise.reject(new Error('Component not found: ' + p));
    return imp();
}
export { }