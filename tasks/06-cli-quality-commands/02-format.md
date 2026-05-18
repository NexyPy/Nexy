# `nexy format` — Unified Formatting

## Goal
Single command that auto-formats all file types in a Nexy project.

## Details

| File Type | Tool | Command |
|-----------|------|---------|
| `.py` | ruff | `ruff format src/` |
| `.ts` / `.tsx` / `.vue` / `.svelte` | prettier | `prettier --write src/` |
| `.nexy` / `.mdx` | Custom | Parse frontmatter → ruff format Python → prettier HTML template → reassemble |

## Implementation

```python
# nexy/cli/commands/format.py
def format_() -> None:
    # 1. Format Python (.py)
    # 2. Format JS/TS (.ts/.tsx/.vue/.svelte)
    # 3. Parse .nexy/.mdx, extract Python frontmatter + HTML template, format each, reassemble
    pass
```

## .nexy/.mdx Format Strategy
1. Read file, split by `---` delimiter
2. Extract Python frontmatter block
3. Extract template block (remaining content)
4. Run `ruff format` on Python block
5. Run `prettier` on template block (HTML)
6. Reassemble with `---` separators
7. Overwrite file

## Detection Logic
- Skip if tool isn't available (e.g., no prettier in node_modules → skip JS files)
- Skip if no files of that type exist
- `.nexy`/`.mdx` formatting always runs (no external tool needed for the split/merge)

## Success Criteria
- `nexy format` formats all files in-place
- `.nexy`/`.mdx` files remain valid after format (compile check passes)
- Returns non-zero exit code on failure
