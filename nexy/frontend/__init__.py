from pathlib import Path
import shutil
from nexy.utils.console import console
from nexy.core.config import Config
from .preact import preact
from .react import react
from .svelte import svelte
from .vue import vue
from .solid import solid

class FrontendGenerator:
    def __init__(self) -> None:
        self.config = Config()
    def generate(self, ssg: bool = False) -> None:
        self._generate_vite_entry()
        self._generate_vite_config()
        if ssg:
            self._generate_ssg()


    def _generate_ssg(self) -> None:
        try:
            import nexy.frontend as frontend
            source = Path(frontend.__file__).parent / "scripts"
            dest = Path("__nexy__") / "scripts"
            shutil.copytree(source, dest, dirs_exist_ok=True)
        except Exception as e:
            print(f"[nexy] Error copying scripts: {e}")
    def _generate_vite_config(self) -> None:
        """Copies the frontend vite config from nexy/frontend/vite.ts to __nexy__/vite.ts."""
        try:
            # On récupère le chemin du fichier source dans le package nexy
            import nexy.frontend as frontend
            source = Path(frontend.__file__).parent / "vite.ts"
            dest = Path("__nexy__") / "vite.ts"
            
            if source.is_file():
                content = source.read_text(encoding="utf-8")
                if not dest.exists() or dest.read_text(encoding="utf-8") != content:
                    dest.write_text(content, encoding="utf-8")
        except Exception as e:
            console.print(f"[red]nsc[/red] » error generating vite.ts: {e}")

    def _generate_vite_entry(self) -> None:
        ff_list = []
        raw_ff = getattr(self.config, "useFF", [])
        if isinstance(raw_ff, list):
            ff_list = raw_ff
        
        frameworks: set[str] = {getattr(ff, "name", "").lower() for ff in ff_list if hasattr(ff, "name")}
        dest_dir = Path("__nexy__")
        src_dir = dest_dir / "src"
        dest_dir.mkdir(parents=True, exist_ok=True)
        src_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "main.ts"

        # Génère les clients useFF (export default run) et l'agrégat ff.auto.ts (imports par défaut + invocation)
        imports: list[str] = []
        invocations: list[str] = []
        for ff in ff_list:
            name = getattr(ff, "name", None)
            render = getattr(ff, "render", None)
            if not name or not render:
                continue
            target = src_dir / f"{name}.nexy.ts"
            content = (
                "const run = () => {\n"
                f"{render}\n"
                "};\n"
                "export default run;\n"
            )
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                target.write_text(content, encoding="utf-8")
            imports.append(f"import init_{name} from './{target.name}';")
            invocations.append(f"init_{name}();")
        ff_auto = src_dir / "ff.auto.ts"
        ff_lines = []
        ff_lines.extend(imports)
        ff_lines.extend(invocations)
        ff_lines.append("export {};")
        ff_content = "\n".join(ff_lines) + "\n"
        if not ff_auto.exists() or ff_auto.read_text(encoding="utf-8") != ff_content:
            ff_auto.write_text(ff_content, encoding="utf-8")
        # keys.auto.ts: mapping hash(md5(path)) -> path
        keys_file = src_dir / "keys.auto.ts"
        mapping: dict[str, str] = {}
        exts = (".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte")
        src_root = Path("src")
        if src_root.is_dir():
            for p in src_root.rglob("*"):
                if p.is_file() and p.suffix.lower() in exts:
                    rel = "/" + p.as_posix().lstrip("/")
                    import hashlib as _h
                    mapping[_h.md5(rel.encode("utf-8")).hexdigest()] = rel
        lines = ["export const __NEXY_KEYS: Record<string,string> = {"]
        for k, v in mapping.items():
            lines.append(f'  "{k}": "{v}",')
        lines.append("};")
        keys_content = "\n".join(lines) + "\n"
        if not keys_file.exists() or keys_file.read_text(encoding="utf-8") != keys_content:
            keys_file.write_text(keys_content, encoding="utf-8")
        runtime = src_dir / "runtime.ts"
        runtime_lines = [
            "type CompMod = { default: unknown }",
            "type Importer = () => Promise<CompMod>",
            "type Importers = Record<string, Importer>",
            "import { __NEXY_KEYS } from '@nexy/keys.auto.ts';",
            "const importers: Importers = import.meta.glob('/src/**/*.{tsx,jsx,ts,js,vue,svelte}', { eager: false }) as Record<string, Importer>",
            "const norm = (p: string) => p && p.startsWith('/') ? p : '/' + p",
            "const w: any = window as any;",
            "w.__nexy_import = (p: string) => {",
            "  let key = p;",
            "  if (!key.startsWith('/')) {",
            "    const mapped = (__NEXY_KEYS as any)[key];",
            "    if (mapped) key = mapped;",
            "  }",
            "  const k1 = norm(key);",
            "  const k2 = k1.startsWith('/') ? k1.slice(1) : k1;",
            "  const imp = (importers as any)[k1] || (importers as any)[k2];",
            "  if (!imp) return Promise.reject(new Error('Component not found: ' + p));",
            "  return imp();",
            "}",
            "export {};",
        ]
        runtime_content = "\n".join(runtime_lines) + "\n"
        if not runtime.exists() or runtime.read_text(encoding="utf-8") != runtime_content:
            runtime.write_text(runtime_content, encoding="utf-8")
        # main.ts minimal: styles globaux + agrégat des clients useFF
        # Dans _generate_vite_entry
        preamble = ""
        if "react" in frameworks:
            preamble = (
                "// Nexy: Synchronous Preamble Injection\n"
                "if (import.meta.env.DEV) {\n"
                "  (window as any).$RefreshReg$ = () => {};\n"
                "  (window as any).$RefreshSig$ = () => (type: any) => type;\n"
                "  (window as any).__vite_plugin_react_preamble_installed__ = true;\n"
                "  import('/@react-refresh').then(m => m.default.injectIntoGlobalHook(window));\n"
                "}\n"
            )

        # IMPORTANT : Le préambule doit être TOUT EN HAUT, avant même les CSS
        minimal = (
            f"{preamble}\n"
            f'import "/src/globale.css";\n'
            f'import "@nexy/runtime.ts";\n'
            f'import "@nexy/ff.auto.ts";\n'
            f"export {{}};\n"
        )

        if not dest.exists() or dest.read_text(encoding="utf-8") != minimal:
            dest.write_text(minimal, encoding="utf-8")



__all__ = [
    "preact",
    "react",
    "svelte",
    "vue",
    "solid",
]
