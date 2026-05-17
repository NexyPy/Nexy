# Task 20: Faster Python import hot reload via `importlib.reload`

## Problem
Changing a `.py` file in `src/` triggers full Uvicorn restart (2-3s). All in-memory state lost.

## Target
Changing a `.py` file → selective `importlib.reload()` of the changed module only (no process restart). Sub-100ms.

## Implementation

### Step 1: Create `nexy/utils/hmr.py`

```python
"""Hot module reloading — selectively reload changed Python modules."""

import importlib
import sys
from pathlib import Path
from typing import Optional


class HotReloader:
    """Selective Python module reloader — reloads only changed modules."""

    _reloaded_modules: set[str] = set()
    _failed_modules: set[str] = set()

    @classmethod
    def reload_module(cls, file_path: str) -> Optional[str]:
        """Reload a single Python module by file path.

        Returns the module name if reloaded, None if not found in sys.modules.
        """
        abs_path = Path(file_path).resolve()

        for name, module in list(sys.modules.items()):
            if module is None:
                continue
            try:
                mod_file = getattr(module, "__file__", None)
                if mod_file and Path(mod_file).resolve() == abs_path:
                    importlib.reload(module)
                    cls._reloaded_modules.add(name)
                    cls._failed_modules.discard(name)
                    return name
            except Exception as e:
                cls._failed_modules.add(name)
                print(f"[hmr] error reloading {name}: {e}")

        return None

    @classmethod
    def needs_full_reload(cls, file_path: str) -> bool:
        """Returns True if the change requires a full Uvicorn restart.

        Full reload needed for:
        - New modules (not yet in sys.modules)
        - Changes to __init__.py files
        - Changes to module dependencies
        """
        p = Path(file_path)
        if p.name == "__init__.py":
            return True
        if cls.reload_module(file_path) is None:
            return True
        return False
```

### Step 2: Integrate via the watcher

In `nexy/utils/watcher.py`, after a `.py` change is detected:

```python
from nexy.utils.hmr import HotReloader

def on_modified(self, event: FileSystemEvent) -> None:
    path = self._normalize(event.src_path)
    
    if path.endswith(".py"):
        if not HotReloader.needs_full_reload(path):
            # Hot reload succeeded — just notify Vite to refresh browser
            if self.on_reload_api:
                self._trigger_vite_reload(path)
        else:
            # Fall back to Uvicorn full restart
            print(f"[hmr] full reload needed for {path}")
    
    elif path.endswith((".nexy", ".mdx")):
        # Recompile and trigger browser refresh
        try:
            start = time.perf_counter()
            self.compiler.compile(input=path)
            elapsed = time.perf_counter() - start
            print(f"[green]nsc[/green] » compiled {path} in {elapsed:.2f}s")
            if self.on_reload_api:
                self._trigger_vite_reload(path)
        except Exception as e:
            print(f"[red]✘ error compiling {path}: {e}[/red]")
```

### Step 3: Write tests in `tests/unit/nexy/utils/test_hmr.py`

```python
import pytest


def test_hot_reloader_reloads_loaded_module():
    from nexy.utils.hmr import HotReloader
    import nexy.core.string
    result = HotReloader.reload_module(nexy.core.string.__file__)
    assert result == "nexy.core.string"


def test_hot_reloader_returns_none_for_new_file():
    from nexy.utils.hmr import HotReloader
    result = HotReloader.reload_module("/nonexistent/module.py")
    assert result is None


def test_needs_full_reload_for_init_py():
    from nexy.utils.hmr import HotReloader
    assert HotReloader.needs_full_reload("some/__init__.py") is True


def test_needs_full_reload_for_new_module():
    from nexy.utils.hmr import HotReloader
    assert HotReloader.needs_full_reload("/tmp/new_module.py") is True
```

## Verify commands

```bash
ruff check nexy/utils/hmr.py
python -m mypy nexy/utils/hmr.py --strict
python -m pytest tests/unit/nexy/utils/test_hmr.py -v
python -m pytest tests/ -v

# Integration test:
# 1. Start nx dev
# 2. Modify a .py file in nexy/ that's already loaded
# 3. Observe: "hmr reloaded nexy.core.xxx" message
# 4. Browser refreshes (no full Uvicorn restart)
```

## Definition of Done
- [ ] `HotReloader.reload_module()` finds and reloads a loaded module
- [ ] `needs_full_reload()` returns True for `__init__.py` and new modules
- [ ] Changing a `.py` module → `importlib.reload()` instead of full restart
- [ ] Changing a `.nexy` file → recompile + browser refresh via Vite WS
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — all pass
