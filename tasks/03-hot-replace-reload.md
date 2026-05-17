# Hot-Module Replacement (HMR) — Replace, Don't Reload

**Goal**: When a `.nexy` or `.py` file changes, Vite HMR should replace only the affected module, not perform a full page reload.

## Problem

Currently `nx dev` watches files and triggers a full page reload on every change. This breaks developer flow for UI iteration.

## Solution architecture

### 1. Server-side change detection
- `watchdog` already watches files — extend `nexy/cli/commands/utilities/watcher.py` to emit structured events:
  ```python
  @dataclass
  class FileChangeEvent:
      path: str
      kind: Literal["route", "component", "template", "config"]
  ```

### 2. WebSocket push to Vite client
- A WebSocket endpoint (`/__nexy_hmr`) pushes change metadata to the browser
- Vite's `handleHotUpdate` hook in `nexy/frontend/vite.ts` intercepts the event and calls:
  - `module.hot.accept()` for component changes
  - `module.hot.invalidate()` for route changes
  - `location.reload()` only as fallback for config/global changes

### 3. Per-module invalidation
- **Component change** (`.nexy` file in `components/`): accept the module — React/Vue/Svelte HMR re-renders in place, preserves state
- **Route change** (`.nexy` / `.py` in `routes/`): invalidate + re-import — the page content swaps without full reload
- **Config change** (`nexyconfig.py`): full reload (page state depends on config)
- **Template change** (`.jinja` or HTML in a `.nexy` template section): accept + re-render the specific component

### 4. Frontend framework integration
Each adapter in `nexy/frontend/{react,vue,svelte,solid,preact}.py` registers framework-specific HMR boundaries:
- **React**: `@vitejs/plugin-react` + `react-refresh` — works out of the box with per-module accept
- **Vue**: `@vitejs/plugin-vue` — SFC HMR built-in
- **Svelte**: `@sveltejs/vite-plugin-svelte` — HMR via `svelte-hmr`
- **Solid**: `vite-plugin-solid` — HMR via `solid-refresh`

The Nexy layer must ensure the generated entry file per route calls the right `import.meta.hot.accept()`.

## Testing

| Test | Scenario |
|------|----------|
| `test_hmr_component_replace` | Change a `.nexy` component → WebSocket pushes update, no reload |
| `test_hmr_route_invalidate` | Change a route file → module invalidated, re-imported |
| `test_hmr_config_reload` | Change `nexyconfig.py` → full page reload |
| `test_hmr_ws_push` | File change → WS message received by Vite client |

## Files to create / modify

- `nexy/cli/commands/utilities/watcher.py` — structured events
- `nexy/cli/commands/utilities/hmr.py` — WebSocket server
- `nexy/frontend/vite.ts` — `handleHotUpdate` hook
- `nexy/frontend/hmr.ts` — client-side HMR handler
- `nexy/cli/commands/dev.py` — wire WS into dev server
- `tests/unit/nexy/watcher/test_hmr.py`
