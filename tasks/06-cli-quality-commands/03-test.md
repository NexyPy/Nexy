# `nexy test` — Unified Testing

## Goal
Single command that runs tests across Python (server) and JS/TS (client).

## Details

| Flag | Layer | Tool | Command |
|------|-------|------|---------|
| `--server` (default) | Python | pytest | `pytest tests/ -v` |
| `--client` | JS/TS | vitest | `npx vitest run` |
| (no flag) | Both | both | pytest + vitest sequentially |

## Implementation

```python
# nexy/cli/commands/test.py
def test(
    server: bool = typer.Option(True, "--server"),
    client: bool = typer.Option(False, "--client"),
) -> None:
    if server:
        subprocess.run(["pytest", "tests/", "-v"])
    if client:
        subprocess.run(["npx", "vitest", "run"])
```

## Detection Logic
- `--client` flag requires vitest to be available (check `vitest.config.ts` or vitest in package.json)
- `--server` flag requires pytest (always available if nexy is installed)
- If no flag provided, run both

## Success Criteria
- `nexy test --server` runs pytest
- `nexy test --client` runs vitest
- `nexy test` runs both
- Non-zero exit code on test failure
- Clean output with pass/fail summary
