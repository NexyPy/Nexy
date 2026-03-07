
import os
from pathlib import Path
from nexy.core.models import PaserModel
from .logic import LogicGenerator
from .template import TemplateGenerator
from nexy.utils.console import console
from nexy.errors import NexyCompileError
from nexy.core.config import Config


class Generator:
    def __init__(self) -> None:
        self.output: str = ""
        self.source: PaserModel | None = None
        self.template = TemplateGenerator()
        self.logic = LogicGenerator()

    def generate(self, output: str, source: PaserModel) -> bool:
        self.source = source
        try:
            directory = os.path.dirname(output)
            if directory:
                os.makedirs(directory, exist_ok=True)
            self.logic.generate(template_path=output, source=self.source)
            self.template.generate(output=output, source=self.source.template)
            self._generate_init(directory)
            self._sync_ff_clients_and_main()
            return True
        except Exception as e:
            console.print(f"[red]nsc[/red] » Error writing to file '{output}': {e}")
            raise NexyCompileError(source_path=output, message=str(e))
    
    def _generate_init(self, directory: str) -> None:
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("")

    def _sync_ff_clients_and_main(self) -> None:
        cfg = Config()
        main_dir = Path("__nexy__")
        src_dir = main_dir / "src"
        main_dir.mkdir(parents=True, exist_ok=True)
        src_dir.mkdir(parents=True, exist_ok=True)

        imports: list[str] = []

        ff_list = getattr(cfg, "nexy_config", None)
        ff_list = getattr(ff_list, "useFF", None) if ff_list else None
        if ff_list:
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
                # Default import and invoke pattern for the aggregator colocated in src/
                imports.append(f"import init_{name} from './{name}.nexy.ts';")
                imports.append(f"init_{name}();")

        if not imports:
            root = Path(".")
            engines = list(root.rglob("*.nexy.ts"))
            if engines:
                engine = engines[0]
                rel = os.path.relpath(engine.as_posix(), start=src_dir.as_posix()).replace("\\", "/")
                target = src_dir / Path(rel).name
                if not target.exists() or target.read_text(encoding="utf-8") != engine.read_text(encoding="utf-8"):
                    target.write_text(engine.read_text(encoding="utf-8"), encoding="utf-8")
                imports.append(f"import './{target.name}';")

        # Écrit un agrégat auto-généré: __nexy__/src/ff.auto.ts
        ff_auto = src_dir / "ff.auto.ts"
        ff_content = "\n".join(imports) + ("\n" if imports else "") + "export {};\n"
        if not ff_auto.exists() or ff_auto.read_text(encoding="utf-8") != ff_content:
            ff_auto.write_text(ff_content, encoding="utf-8")
        # keys.auto.ts map
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

        # Garantit que __nexy__/main.ts importe l’agrégat auto
        main_ts = main_dir / "main.ts"
        runtime_ts = src_dir / "runtime.ts"
        runtime_body = (
            "type CompMod = { default: unknown }\n"
            "type Importer = () => Promise<CompMod>\n"
            "type Importers = Record<string, Importer>\n"
            "import { __NEXY_KEYS } from 'nexy:keys.auto.ts'\n"
            "const importers: Importers = import.meta.glob('/src/**/*.{tsx,jsx,ts,js,vue,svelte}', { eager: false }) as Record<string, Importer>\n"
            "const norm = (p: string) => p && p.startsWith('/') ? p : '/' + p\n"
            "const w: any = window as any;\n"
            "(async () => {\n"
            "  try {\n"
            "    if (import.meta && (import.meta as any).env && (import.meta as any).env.DEV) {\n"
            "      const mod: any = await import('/@react-refresh');\n"
            "      const RefreshRuntime = mod && mod.default;\n"
            "      if (RefreshRuntime && typeof RefreshRuntime.injectIntoGlobalHook === 'function') {\n"
            "        RefreshRuntime.injectIntoGlobalHook(w);\n"
            "        w.$RefreshReg$ = () => {};\n"
            "        w.$RefreshSig$ = () => (type: unknown) => type;\n"
            "        w.__vite_plugin_react_preamble_installed__ = true;\n"
            "      }\n"
            "    }\n"
            "  } catch { /* ignore */ }\n"
            "})();\n"
            "w.__nexy_import = (p: string) => {\n"
            "  let key = p;\n"
            "  if (!key.startsWith('/')) {\n"
            "    const mapped = (__NEXY_KEYS as any)[key];\n"
            "    if (mapped) key = mapped;\n"
            "  }\n"
            "  const k1 = norm(key);\n"
            "  const k2 = k1.startsWith('/') ? k1.slice(1) : k1;\n"
            "  const imp = (importers as any)[k1] || (importers as any)[k2];\n"
            "  if (!imp) return Promise.reject(new Error('Component not found: ' + p));\n"
            "  return imp();\n"
            "}\n"
            "export {};\n"
        )
        if not runtime_ts.exists() or runtime_ts.read_text(encoding="utf-8") != runtime_body:
            runtime_ts.write_text(runtime_body, encoding="utf-8")
        import_line = "import 'nexy:runtime.ts';\nimport 'nexy:ff.auto.ts';"
        if main_ts.exists():
            content = main_ts.read_text(encoding="utf-8")
            if import_line not in content:
                main_ts.write_text(content.rstrip() + "\n" + import_line + "\n", encoding="utf-8")
        else:
            main_ts.write_text(import_line + "\nexport {};\n", encoding="utf-8")


__all__ = ["Generator"]
