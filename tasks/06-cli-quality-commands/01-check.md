# `nexy check` — Unified Type Checking

## Goal
Single command that runs type checking across all file types in a Nexy project.

## Details

| File Type | Tool | Command |
|-----------|------|---------|
| `.py` | mypy | `mypy src/` (or `mypy .`) |
| `.ts` / `.tsx` / `.vue` / `.svelte` | tsc | `tsc -b` (uses tsconfig.json) |
| `.nexy` / `.mdx` | nsc + mypy | Compile via Builder → `mypy __nexy__/` |

## Implementation

```python
# nexy/cli/commands/check.py
def check() -> None:
    # 1. Check Python (.py)
    # 2. Check TypeScript (.ts/.tsx/.vue/.svelte)
    # 3. Compile .nexy/.mdx then check generated Python
    pass
```

## Detection Logic
- Skip if tool isn't available (e.g., no tsconfig.json → skip tsc)
- Skip if no files of that type exist
- Run everything, collect failures, print summary at end

## Success Criteria
- `nexy check` runs mypy + tsc + nsc+mypy with clear output
- Returns non-zero exit code on any failure
- Shows per-section summary (Python OK, TypeScript 3 errors, Nexy OK)
