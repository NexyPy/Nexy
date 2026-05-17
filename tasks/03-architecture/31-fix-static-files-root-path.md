# Task 31: Fix static files serving at root path `/`

## Problem

`nexy/routers/app.py:_setup_static_files()` mounts the `public/` directory at URL path `/public`. This is inconsistent with Vercel and most modern frameworks, where `public/` contents are served at the root `/` (e.g., `public/vite.svg` → `/vite.svg`).

Current code:
```python
mounts = {
    "/public": "public",
    "/assets": "__nexy__/client/assets"
}
```

## Changes

### `nexy/routers/app.py` — Mount `public/` at root `/`

```python
# Before (lines 52-58):
def _setup_static_files(self):
    mounts = {
        "/public": "public",
        "/assets": "__nexy__/client/assets"
    }
    for path, directory in mounts.items():
        if os.path.isdir(directory):
            self.server.mount(path, StaticFiles(directory=directory), name=directory)

# After:
def _setup_static_files(self):
    # Mount public/ at root so files are accessible as /filename.ext
    # Must be mounted after routes to avoid conflicts
    if os.path.isdir("public"):
        self.server.mount("/", StaticFiles(directory="public", check_dir=False), name="public")
    # Mount build assets
    assets_dir = "__nexy__/client/assets"
    if os.path.isdir(assets_dir):
        self.server.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
```

**Important**: Starlette's `StaticFiles` with `check_dir=False` at `"/"` lets FastAPI routes take precedence. Routes registered after this mount will still work because FastAPI registers routes in order and Starlette's `Mount` only handles paths not matched by previous routes.

### Alternative: Mount after all routes

If mounting at `/` causes issues, mount public files at `"/"` after all routes are registered. Move `_setup_static_files()` call to after `_resolve_router()` in the `run()` method.

```python
# In run() method, lines 137-141:
self.server.middleware("http")(self.PathMiddleware)
self._setup_favicon()
self._resolve_router()           # Routes registered first
self._setup_static_files()       # Then static files as fallback
self.server.exception_handler(HTTPException)(self._register_error_handlers)
```

## Search commands

```bash
rg "_setup_static_files" nexy/routers/app.py
rg "StaticFiles" nexy/routers/
rg "/public" nexy/
```

## Verify

- [ ] `public/vite.svg` is accessible at `http://localhost:3000/vite.svg` (not `/public/vite.svg`)
- [ ] API routes still work (static files don't shadow routes)
- [ ] `public/` directory doesn't exist → no crash, no mount
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m pytest tests/ -v` — no regressions
