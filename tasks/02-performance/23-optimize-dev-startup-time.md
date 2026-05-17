# Task 23: Optimize dev startup — lazy compilation, sub-second start

## Problem
`nx dev` does a **full `Builder().build()`** before starting the server. On large projects this adds 3-10s before the dev server is ready. Vite starts in ~300ms. Nexy should too.

**Target:** `nx dev` shows "ready" message in <500ms (excluding compile time).

## Solution: Lazy compilation

The dev server starts **before** compiling anything. Compilation happens:
1. On first HTTP request (compile the requested route only)
2. On file change during watch (incremental, full or partial)

### Step 1: Read current files

```bash
Get-Content -LiteralPath "nexy/cli/commands/dev.py"
Get-Content -LiteralPath "nexy/routers/app.py" | Select-Object -First 100
Get-Content -LiteralPath "nexy/compiler/__init__.py"
```

### Step 2: Modify `nexy/cli/commands/dev.py`

**Change the startup sequence:**

Current (approximate):
```python
def dev(...):
    config = get_config()
    # Full build blocks startup
    Builder().build(showlog=True)
    # Then start servers
    Server.uvicorn(...)
    Server.vite(...)
```

New:
```python
def dev(
    port: int = typer.Option(3000, help="Server port"),
    host: str = typer.Option("127.0.0.1", help="Bind address"),
    prebuild: bool = typer.Option(False, "--prebuild", help="Compile all files at startup"),
) -> None:
    """Start development server with instant startup (lazy compilation)."""
    config = get_config()
    
    # Optional full build
    if prebuild:
        console.print("[dim]Pre-building all files...[/dim]")
        Builder().build(showlog=True, incremental=False)
    
    # Start server immediately (lazy compile on first request)
    console.print("[green]Starting dev server (lazy compile mode)[/green]")
    Server.uvicorn(host=host, port=port, as_process=True)
    
    # For Vite (if applicable) — no change needed
    if config.use_vite if hasattr(config, 'use_vite') else False:
        Server.vite(port=_find_available_port(5173))
    
    console.print(f"[green]Ready[/green] at [bold]http://{host}:{port}[/bold]")
```

### Step 3: Add lazy compilation hook in route handling

Modify the route handler (likely in `nexy/routers/fbrouter/__init__.py` or the compiler) to compile on first request.

Find where `.nexy` files are served. There should be a route handler that looks up `.nexy` files and compiles them. Modify it:

```python
class FBRouter:
    _initial_build_done = False
    
    async def _ensure_route_compiled(self, route_path: str) -> None:
        """Lazy compile: build on first request if not already compiled."""
        if not self._initial_build_done:
            self._initial_build_done = True
            # First request: do a full build
            # Builder().build(showlog=True, incremental=False)
        
        # For the specific route, compile if its output doesn't exist
        compiled_path = Path("__nexy__") / route_path.replace(".nexy", ".py")
        if not compiled_path.exists():
            # Single-file compile is faster than full build
            # self.compiler.compile(input=route_path)
            pass
```

**Important:** This depends on the exact router implementation. The key principle is:
- Don't block server start on compilation
- Compile on first request
- The `FBRouter` already exists and handles route matching — just defer the compile step

### Step 4: Measure startup time

Add timing to dev startup:

```python
import time

def dev(...):
    start = time.time()
    # ... start logic ...
    elapsed = time.time() - start
    console.print(f"[green]Ready[/green] in [bold]{elapsed:.2f}s[/bold] at [bold]http://{host}:{port}[/bold]")
```

### Step 5: Handle the "first request is slow" UX

Since the first request will trigger compilation, add a console message:

```python
# In the FBRouter or middleware, before first compile:
console.print("[dim]First request — compiling routes...[/dim]")
```

Also consider compiling the requested route plus its dependencies (parsed from the frontmatter imports), not all files.

## Verify with commands

```bash
# Measure startup time
Measure-Command { nx dev --port 3099 }

# Should show "Ready in 0.3s" (or similar) without --prebuild
# With --prebuild, should show the old full-build startup time

# Test first request:
# Open http://localhost:3099 in browser
# Should see compilation message, then the page loads

python -m pytest tests/ -v
```

## Definition of Done
- [ ] `nx dev` prints "Ready" message in <500ms (no prebuild)
- [ ] `nx dev --prebuild` restores full compilation at startup
- [ ] First HTTP request triggers compilation (visible in console)
- [ ] Subsequent requests use already-compiled files (fast)
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — all pass
