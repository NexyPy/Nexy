# Task 18: Replace cold Uvicorn restart with live reload

## Problem
`nx dev` uses watchdog to **kill and restart** the entire Uvicorn process on every `.py`/`.nexy` change (~2-3s cold restart). All in-memory state lost, full browser page reload.

## Target
Sub-second reload (<500ms for `.py` change, <200ms for `.nexy` change).

## Architecture change

**Before:**
```
watchdog detects change → kill Uvicorn subprocess → Builder.build() → start new Uvicorn subprocess
```

**After:**
```
uvicorn --reload (watchfiles) detects change → uvicorn hot-reloads Python modules
  → Builder.build() compiles only changed .nexy files (no process restart)
```

## Detailed implementation steps

### Step 1: Read current files

Files to read before editing:
- `nexy/cli/commands/dev.py` — the dev command entry point
- `nexy/cli/commands/utilities/server.py` — Server.uvicorn() method
- `nexy/cli/commands/utilities/watcher.py` — WatchHandler class
- `nexy/cli/commands/utilities/uvicorn_config.py` — log config

### Step 2: Modify `nexy/cli/commands/utilities/server.py`

**Replace the `Server.uvicorn()` method:**

Search for the current `def uvicorn(` method definition and the line that imports/configures `_uvicorn`.

Old code (approximate pattern — verify against actual file):
```python
@staticmethod
def uvicorn(
    host: Optional[str] = None,
    port: int = 3000,
    as_process: bool = False,
) -> Optional[Popen]:
    """Lance le serveur FastAPI/Uvicorn avec auto-reload watchdog."""
    run_host = host or "127.0.0.1"
    _write_port_file("server", port)

    if as_process:
        return subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "nexy.routers.app:_server",
             "--host", run_host, "--port", str(port)],
            ...
        )
    else:
        _uvicorn.run(...)
```

New code:
```python
@staticmethod
def uvicorn(
    host: Optional[str] = None,
    port: int = 3000,
    as_process: bool = False,
) -> Optional[Popen]:
    """Start FastAPI/Uvicorn with --reload for instant HMR."""
    run_host = host or "127.0.0.1"
    _write_port_file("server", port)

    reload_dirs = []
    if config:
        reload_dirs.append(str(config.PROJECT_ROOT))
    reload_dirs.append(str(Path(nexy.__file__).parent))

    if as_process:
        return subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn",
                "nexy.routers.app:_server",
                "--host", run_host,
                "--port", str(port),
                "--reload",
                "--reload-dir", str(config.PROJECT_ROOT) if config else ".",
                "--reload-dir", str(Path(nexy.__file__).parent),
                "--reload-include", "*.py",
                "--reload-include", "*.nexy",
                "--reload-include", "*.mdx",
                "--reload-exclude", "__nexy__/*",
                "--log-config", str(NEXY_LOG_CONFIG_PATH),
            ],
            stdout=subprocess.DEVNULL if not NEXY_DEBUG else None,
            stderr=subprocess.DEVNULL if not NEXY_DEBUG else None,
        )
    else:
        _uvicorn.run(
            "nexy.routers.app:_server",
            host=run_host,
            port=port,
            reload=True,
            reload_dirs=[str(config.PROJECT_ROOT) if config else ".", str(Path(nexy.__file__).parent)],
            reload_includes=["*.py", "*.nexy", "*.mdx"],
            reload_excludes=["__nexy__/*"],
            log_config=NEXY_LOG_CONFIG,
        )
```

**Also add at top of file:**
```python
import nexy
from pathlib import Path
```

### Step 3: Modify `nexy/cli/commands/dev.py`

**Remove watchdog setup.** Search for lines that:
1. Import or instantiate `WatchHandler` or `watchdog.observers`
2. Start/stop the watchdog observer

Replace the watchdog-based file watching with a simple Uvicorn launch.

Old pattern (verify actual lines):
```python
from nexy.cli.commands.utilities.watcher import WatchHandler
...
observer = Observer()
handler = WatchHandler()
observer.schedule(handler, str(config.PROJECT_ROOT), recursive=True)
observer.start()
...
Server.uvicorn(host=run_host, port=run_port, as_process=True)
...
observer.stop()
observer.join()
```

New pattern:
```python
# No watchdog needed — uvicorn --reload handles file watching
Server.uvicorn(host=run_host, port=run_port, as_process=True)
```

**Also modify the initial build** to ensure it runs `Builder.build()` on startup (fire-and-forget):
```python
# Initial full build (before server starts serving)
if not prebuild_disabled:
    Builder().build(showlog=True)
```

### Step 4: Simplify `nexy/cli/commands/utilities/watcher.py`

The `WatchHandler` class is no longer needed for Python file watching (uvicorn handles that). However, keep it for coordinating Vite HMR if needed.

Replace most of `watcher.py`:
```python
# Reduced — uvicorn --reload handles Python/.nexy file watching
# This file remains for Vite HMR coordination only

import time
from pathlib import Path
from typing import Callable

class WatchHandler:
    """Minimal handler for triggering non-Python file changes (assets, styles, etc.)."""
    
    def __init__(self, on_change: Callable[[Path], None] | None = None):
        self.on_change = on_change
    
    def dispatch(self, event):
        if self.on_change and not event.is_directory:
            self.on_change(Path(event.src_path))
```

### Step 5: Configure log config for cleaner output

In `nexy/cli/commands/utilities/uvicorn_config.py`:
- The custom `StatusFilter` and `ReadableFormatter` should still be used
- Ensure `--log-config` points to a dict config (not a file path) that suppresses uvicorn's default startup spam

Add:
```python
NEXY_LOG_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "access": {"()": ReadableFormatter},
    },
    "handlers": {
        "default": {"class": "logging.NullHandler"},
        "access": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "WARNING", "propagate": False},
        "uvicorn.error": {"level": "WARNING"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}
```

## Verify with commands

```bash
# Start dev server
nx dev --port 3000

# In another terminal, check that only one uvicorn process exists (not kill+restart loop)
# Test by modifying a .py file — should see fast reload in console
echo "" >> nexy/core/config.py
# Observe: uvicorn reloads in <500ms, no process restart

# Test by modifying a .nexy file
echo "" >> tests/fixtures/test.nexy
# Observe: builder compiles, uvicorn sees new .py output

# Check no watchdog processes
Get-Process -Name "python" | Select-Object Id, ProcessName
```

## Definition of Done
- [ ] `nx dev` starts with single `uvicorn --reload` process (no watchdog subprocess)
- [ ] Changing a `.py` file → uvicorn reload in <500ms
- [ ] Changing a `.nexy` file → `Builder().build()` triggers → uvicorn reload
- [ ] Terminal output is clean (no watchdog logs)
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
