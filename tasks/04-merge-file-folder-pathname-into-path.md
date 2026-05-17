# Task 04: Merge File, Folder, PathName into `pathlib.Path` (then delete)

## Problem
Three tiny utility classes in `nexy/utils/` that do nothing `pathlib.Path` doesn't already do:

- `nexy/utils/file.py` — `File` class: read, write, exists, delete, create
- `nexy/utils/folder.py` — `Folder` class: exists, create, delete, normalize
- `nexy/utils/pathname.py` — `PathName` class: normalize (spaces→underscores, lowercase)

**KISS says: don't wrap what you don't need to.**

## Step 1: Find all usages

```bash
rg "from nexy.utils.file import" nexy/
rg "from nexy.utils.folder import" nexy/
rg "from nexy.utils.pathname import" nexy/
rg "nexy\.utils\.(file|folder|pathname)" nexy/ tests/
```

## Step 2: Replace each usage with `pathlib.Path`

Common replacements:

| Old code | New code |
|----------|----------|
| `File().read(path)` | `Path(path).read_text(encoding="utf-8")` |
| `File().write(path, content)` | `Path(path).write_text(content, encoding="utf-8")` |
| `File().exists(path)` | `Path(path).exists()` |
| `File().delete(path)` | `Path(path).unlink()` |
| `File().create(path)` | `Path(path).touch()` |
| `Folder().exists(path)` | `Path(path).is_dir()` |
| `Folder().create(path)` | `Path(path).mkdir(parents=True, exist_ok=True)` |
| `Folder().delete(path)` | `shutil.rmtree(path)` |
| `PathName().normalize(path)` | `path.replace(" ", "_").lower()` |

## Step 3: Delete the 3 files

```powershell
Remove-Item -LiteralPath "nexy/utils/file.py"
Remove-Item -LiteralPath "nexy/utils/folder.py"
Remove-Item -LiteralPath "nexy/utils/pathname.py"
```

## Verify commands

```bash
# No files remain
Test-Path -LiteralPath "nexy/utils/file.py"      # False
Test-Path -LiteralPath "nexy/utils/folder.py"     # False
Test-Path -LiteralPath "nexy/utils/pathname.py"   # False

# No remaining imports
rg "from nexy.utils.(file|folder|pathname) import" nexy/  # Empty

ruff check nexy/
python -m mypy nexy --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] `nexy/utils/file.py` deleted
- [ ] `nexy/utils/folder.py` deleted
- [ ] `nexy/utils/pathname.py` deleted
- [ ] All usages replaced with inline `pathlib.Path` calls
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
