# Performance: Fastest Python Framework in 2026

**Goal**: Nexy must outperform every existing Python web framework (including FastAPI itself) in request throughput and cold-start time.

## Measurable targets

| Metric | Target | Competitor baseline (FastAPI) |
|--------|--------|-------------------------------|
| Requests/sec (sync) | ≥ 2× FastAPI | 10-15k req/s (uvicorn 1 worker) |
| Requests/sec (async) | ≥ 1.5× FastAPI | 20-25k req/s (uvicorn 1 worker) |
| Cold start (import + first byte) | ≤ 30ms | 80-150ms |
| Memory per request (idle) | ≤ 2 MB overhead | 5-8 MB |
| Startup time `nx dev` | ≤ 200ms | 500ms+ |

## Strategy

### 1. Lazy loading everywhere
- Router discovery is deferred: scan `.nexy` files on first request, not at import
- Frontend framework adapters are lazy-imported only when the framework is used
- Config parsing is lazy — `nexyconfig.py` is evaluated only when first accessed

### 2. Zero-overhead routing
- FastAPI's `APIRouter` adds overhead — benchmark raw ASGI routing vs. Starlette vs. FastAPI
- Consider bypassing FastAPI routing for file-based routes (register raw ASGI apps)
- Use a trie-based router for O(path_length) matching

### 3. Compile-time optimization
- `.nexy` files compile to a cached bytecode-like representation (`__nexy__/cache/`)
- Static routes are pre-compiled at `nx build`, loaded as pickle at runtime
- Jinja2 templates are pre-compiled with `jinja2.Environment(optimized=True)`

### 4. Minimal middleware stack
- Remove all optional middleware by default
- `useDocs`, `useScalar`, `useCORS` etc. are opt-in, not on by default
- Measure the cost of each middleware layer individually

### 5. ASGI server tuning
- Default to `uvicorn --workers=$(nproc) --loop=uvloop --http=httptools`
- Allow override via `nx start --server granian` or `nx start --server hypercorn`
- Ensure `NexyConfig` exposes `useServer: str | dict`

## Benchmark harness

- Use `k6` or `oha` for HTTP load testing
- `tests/performance/bench_*.py` using `pytest-benchmark`
- CI gate: `make perf` must not regress > 5%

## Files to create / modify

- `tests/performance/__init__.py`
- `tests/performance/test_latency.py`
- `tests/performance/test_throughput.py`
- `nexy/core/config.py` — add `useServer` option
- `nexy/cli/commands/start.py` — server selection logic
- `nexy/routers/app.py` — lazy init, minimal middleware
- `nexy/compiler/cache.py` — compiled route cache
