# Server Hooks API

**Goal**: Provide ergonomic server-side hooks (`usePathname()`, `useStatus()`, etc.) that feel familiar to frontend developers while running entirely on the FastAPI side.

## Requirements

- `usePathname()` → returns the current request URL path
- `useStatus()` → returns the HTTP status code of the response
- `useHeaders()` → returns request headers as a dict
- `useCookies()` → returns request cookies as a dict
- `useQuery()` → returns parsed query parameters
- `useParams()` → returns route path parameters
- `useForm()` → returns parsed form data (multipart or URL-encoded)

## Design constraints (KISS + SOLID)

- Each hook is a standalone callable in `nexy/runtime/hooks/` (one file per hook)
- Hooks pull data from the current `Request` context — use FastAPI's `request: Request` injection or a contextvar
- No base class inheritance maze; a hook is just a function with a `@hook` marker or a simple convention
- `use*` naming reserved for runtime hooks — document this clearly

## Async/all

- Hooks must work in both sync and async route handlers
- If data isn't available (e.g., `useForm()` outside a form POST), raise a clear `RuntimeError` with a message explaining the missing context

## Testing (TDD)

| Test | Scenario |
|------|----------|
| `test_use_pathname_returns_path` | GET `/hello` → `usePathname()` == `"/hello"` |
| `test_use_status_in_handler` | Handler returns 201 → `useStatus()` == `201` |
| `test_use_form_outside_post` | GET request → `useForm()` raises `RuntimeError` |
| `test_use_query_with_params` | `?page=2&q=foo` → `useQuery()` == `{"page": "2", "q": "foo"}` |

## Files to create / modify

- `nexy/runtime/hooks/__init__.py` — public API, exports all hooks
- `nexy/runtime/hooks/pathname.py`
- `nexy/runtime/hooks/status.py`
- `nexy/runtime/hooks/headers.py`
- `nexy/runtime/hooks/cookies.py`
- `nexy/runtime/hooks/query.py`
- `nexy/runtime/hooks/params.py`
- `nexy/runtime/hooks/form.py`
- `nexy/runtime/context.py` — contextvar for the current request
- `nexy/routers/app.py` — inject context middleware
- `tests/unit/nexy/runtime/test_hooks.py`
