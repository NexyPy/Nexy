# Task 22: Dev server status bar with timings

## Problem
`nx dev` output has no sense of speed or health. Compare with Vite's clean output:
- Server startup time
- Compilation time per file
- Total compiled count
- URLs

## Implementation

### Step 1: Create `nexy/utils/status.py`

```python
"""Dev server status display — timings, counts, URLs."""

import time
from dataclasses import dataclass, field


@dataclass
class DevStatus:
    """Live-updating status tracker for the dev server."""

    start_time: float = field(default_factory=time.time)
    compiled_count: int = 0
    error_count: int = 0
    file_count: int = 0
    last_event: str = ""
    last_event_time: float = 0.0
    server_url: str = ""
    vite_url: str = ""

    def elapsed(self) -> float:
        return time.time() - self.start_time

    def on_compiled(self, path: str, duration: float) -> None:
        self.compiled_count += 1
        self.last_event = f"compiled {path} in {duration:.2f}s"
        self.last_event_time = time.time()

    def on_error(self, path: str, error: str) -> None:
        self.error_count += 1
        self.last_event = f"error in {path}: {error}"
        self.last_event_time = time.time()

    def summary(self) -> str:
        parts = [
            f"[bold green]Nexy[/bold green]",
            f"up {self.elapsed():.1f}s",
            f"compiled {self.compiled_count} files",
        ]
        if self.error_count:
            parts.append(f"[red]{self.error_count} errors[/red]")
        else:
            parts.append("0 errors")
        if self.server_url:
            parts.append(f"server: {self.server_url}")
        if self.vite_url:
            parts.append(f"vite: {self.vite_url}")
        return " · ".join(parts)

    def startup_banner(self) -> str:
        """Returns the startup banner panel."""
        from rich.panel import Panel
        from rich import box

        info = []
        if self.server_url:
            info.append(f"  [bold]Server:[/bold]  {self.server_url}")
        if self.vite_url:
            info.append(f"  [bold]Vite:[/bold]    {self.vite_url}")
        info.append(f"  [bold]Docs:[/bold]    {self.server_url}/docs" if self.server_url else "")
        info.append("")
        info.append("  [dim]Press Ctrl+C to stop[/dim]")

        return Panel.fit(
            "\n".join(info),
            title=f"[bold green]Nexy[/bold green]",
            border_style="green",
            box=box.ROUNDED,
        )
```

### Step 2: Modify `nexy/cli/commands/dev.py`

Add timing to the dev startup sequence:

```python
import time
from nexy.utils.status import DevStatus

def dev(...) -> None:
    status = DevStatus()
    start = time.time()
    
    # ... startup logic ...
    
    # After determining ports:
    status.server_url = f"http://{host}:{port}"
    status.vite_url = f"http://localhost:{client_port}" if client_port else ""
    
    # Print startup banner
    console.print(status.startup_banner())
    
    # Show elapsed startup time
    startup_elapsed = time.time() - start
    console.print(f"[dim]Started in {startup_elapsed:.2f}s[/dim]")
```

### Step 3: Add timing to compilation output

In the builder or watcher, time each compilation:

```python
import time

start = time.perf_counter()
# ... compile call ...
elapsed = time.perf_counter() - start
status.on_compiled(path, elapsed)
```

### Step 4: Replace raw console prints with status updates

Find all `console.print(f"[green]nsc[/green] » compiled ..."` patterns and replace with:
```python
console.print(f"[green]nsc[/green] » compiled [dim]{path}[/dim] in [green]{elapsed:.2f}s[/green] [green]✓[/green]")
```

And error prints with:
```python
console.print(f"[red]nsc[/red] » error compiling [dim]{path}[/dim] [red]✗[/red]")
```

## Verify commands

```bash
# Check startup banner
# Start nx dev and look for:
# ┌─ Nexy ─────────────────────────────┐
# │   Server:  http://127.0.0.1:3000   │
# │   Vite:    http://localhost:5173    │
# │   Docs:    http://127.0.0.1:3000/docs │
# │                                    │
# │   Press Ctrl+C to stop             │
# └────────────────────────────────────┘
# Started in 0.3s

ruff check nexy/utils/status.py
python -m mypy nexy/utils/status.py --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] `nx dev` shows clean startup banner with URLs and version
- [ ] Compilation events show file path + timing (e.g. "compiled src/index.nexy in 0.12s")
- [ ] Errors shown in red with file path
- [ ] Startup elapsed time shown
- [ ] No raw markup tags (`[green]...[/green]`) visible in terminal
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — all pass
