# Task 24: Fix Vite HMR coordination — explicit reload signal

## Problem
When a `.nexy` file changes, the browser refresh depends on Vite polling the filesystem for changes to compiled output in `__nexy__/`. This has a race condition: the page may reload before the new compile output is ready, showing stale content.

## Target
Browser refresh fires **after** compilation completes. Explicit POST from Python to Vite WS triggers the reload. No polling, no race.

## Implementation

### Step 1: Create/Modify `nexy/utils/hmr.py` (add Vite reload trigger)

Add to the `hmr.py` created in Task 20:

```python
import httpx
from typing import Optional


async def trigger_vite_reload(
    vite_port: int = 5173,
    path: str = "",
    reload_type: str = "full-reload",
) -> bool:
    """Send reload signal to Vite dev server.

    Uses Vite's custom HMR endpoint. Returns True if signal was sent.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"http://localhost:{vite_port}/__nexy_hmr",
                json={"path": path, "type": reload_type},
                timeout=2.0,
            )
            return resp.status_code == 200
    except httpx.ConnectError:
        return False  # Vite not ready yet
    except Exception:
        return False
```

### Step 2: Modify Vite plugin (`nexy/frontend/vite.ts`)

Add custom HMR endpoint to the Vite plugin. Find or create the `nexy()` Vite plugin.

```typescript
// In the nexy() Vite plugin definition
import { Plugin, ViteDevServer } from 'vite'

export function nexy(options?: NexyOptions): Plugin {
  return {
    name: 'nexy-hmr',
    configureServer(server: ViteDevServer) {
      // Custom endpoint for Python to trigger reloads
      server.middlewares.use('/__nexy_hmr', (req, res) => {
        if (req.method !== 'POST') {
          res.statusCode = 405
          res.end('Method Not Allowed')
          return
        }
        
        let body = ''
        req.on('data', (chunk: string) => (body += chunk))
        req.on('end', () => {
          try {
            const data = JSON.parse(body)
            // Send full-reload to all connected browser clients
            server.ws.send({
              type: 'full-reload',
              path: data.path || '*',
            })
            res.statusCode = 200
            res.end('reload sent')
          } catch (e) {
            res.statusCode = 400
            res.end(`Invalid JSON: ${e}`)
          }
        })
      })
    },
  }
}
```

### Step 3: Modify watcher to call Vite reload

In `nexy/utils/watcher.py`, after compilation, trigger the Vite reload:

```python
def _trigger_vite_reload(self, path: str) -> None:
    """Tell Vite to reload the browser after compilation."""
    from nexy.utils.hmr import trigger_vite_reload
    import asyncio
    
    try:
        asyncio.run(trigger_vite_reload(
            vite_port=get_client_port(5173),
            path=path,
        ))
    except Exception:
        pass  # Non-critical — browser will eventually reload
```

### Step 4: Wire up in dev.py

In `nexy/cli/commands/dev.py`, pass the Vite port to the watcher:

```python
from nexy.utils.hmr import trigger_vite_reload

# After compilation:
asyncio.run(trigger_vite_reload(
    vite_port=client_port or 5173,
    path=input_path,
))
```

## Verify commands

```bash
# Start dev server, open browser
# Edit a .nexy file → should see immediate browser refresh
# Check terminal: "hmr → reload signal sent to Vite"

ruff check nexy/utils/hmr.py
# pnpm typecheck in extensions/vscode or root if applicable
python -m pytest tests/ -v
```

## Definition of Done
- [ ] Changing a `.nexy` file → immediate browser refresh (no polling delay)
- [ ] Changing a `.py` file → browser refresh via explicit signal
- [ ] No duplicate reloads (one from WS signal + one from file watching)
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — all pass
