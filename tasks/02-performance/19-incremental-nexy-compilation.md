# Task 19: Incremental .nexy compilation with MD5 cache

## Problem
`Builder().build()` recompiles **every** `.nexy`/`.mdx` file even if only one file changed. On 100+ components → 3-10s per build.

**Target:** Second+ builds compile only changed files in <100ms overhead.

## Solution: MD5-based content cache

### Step 1: Read current files

```bash
Get-Content -LiteralPath "nexy/builder/__init__.py" | Select-Object -First 80
Get-Content -LiteralPath "nexy/builder/cache.py" | Select-Object -First 40
```

If `nexy/builder/cache.py` does not exist, create it. If it exists as a stub, replace its content.

### Step 2: Create/Replace `nexy/builder/cache.py`

```python
import hashlib
import json
from pathlib import Path

CACHE_FILE = Path("__nexy__/build.cache.json")


class BuildCache:
    _cache: dict[str, str] = {}

    @classmethod
    def load(cls) -> None:
        if CACHE_FILE.exists():
            cls._cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))

    @classmethod
    def save(cls) -> None:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(
            json.dumps(cls._cache, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    @classmethod
    def is_changed(cls, path: str | Path) -> bool:
        p = Path(path).resolve()
        if not p.is_file():
            return True
        curr_hash = hashlib.md5(p.read_bytes()).hexdigest()
        prev_hash = cls._cache.get(str(p))
        return curr_hash != prev_hash

    @classmethod
    def mark_built(cls, path: str | Path) -> None:
        p = Path(path).resolve()
        if p.is_file():
            cls._cache[str(p)] = hashlib.md5(p.read_bytes()).hexdigest()

    @classmethod
    def clear(cls) -> None:
        cls._cache = {}
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
```

### Step 3: Modify `nexy/builder/__init__.py`

Find the `Builder.build()` method. The exact location and code depends on what's currently there. Make these changes:

**Add import at top:**
```python
from nexy.builder.cache import BuildCache
```

**Modify `build()` method to use cache:**
The method currently iterates over files and compiles each one. Add cache check before compilation:

```python
def build(self, showlog: bool = False, incremental: bool = True) -> None:
    """Build all discovered .nexy/.mdx files.
    
    Args:
        showlog: Print compilation status per file.
        incremental: Skip unchanged files (MD5 cache).
    """
    BuildCache.load()
    files = self.discovery.scan(self.config.PROJECT_ROOT)
    errors: list[tuple[str, str]] = []
    
    for file in files:
        input_path = file.as_posix()
        
        # Skip unchanged files in incremental mode
        if incremental and not BuildCache.is_changed(input_path):
            continue
        
        try:
            # Find the actual compile call — exact method name/signature
            # may be self.compiler.compile(input=input_path) or similar
            self.compiler.compile(input=input_path)
            BuildCache.mark_built(input_path)
            if showlog:
                console.print(
                    f"[green]nsc[/green] » compiled "
                    f"[reset][dim]{input_path}[/dim] [green]✓[/green]"
                )
        except Exception as e:
            errors.append((input_path, str(e)))
            if showlog:
                console.print(
                    f"[red]nsc[/red] » error compiling "
                    f"[reset][dim]{input_path}[/dim] [red]✗[/red]"
                )
    
    BuildCache.save()
    
    if errors and not incremental:
        raise RuntimeError(f"Build failed: {len(errors)} error(s)")
```

**Handle the `incremental` parameter:**
- In `nx dev`: use `incremental=True` for watch-triggered builds, `incremental=False` for initial build
- In `nx build`: always `incremental=False`

### Step 4: Modify `nexy/cli/commands/dev.py`

Find the initial build call and subsequent watch-triggered builds:

```python
# Initial build at startup (full build)
Builder().build(showlog=True, incremental=False)

# On subsequent file changes (triggered by uvicorn reload hook):
# ← After detecting a .nexy change:
# Builder().build(showlog=True, incremental=True)
```

### Step 5: Modify `nexy/cli/commands/build.py`

Find the production build call and ensure it does full build:
```python
# Always full build in production
Builder().build(showlog=True, incremental=False)
BuildCache.clear()  # Clear cache for fresh production build
```

## Write tests in `tests/unit/nexy/builder/test_cache.py`

```python
import pytest
from pathlib import Path
from nexy.builder.cache import BuildCache


@pytest.fixture
def temp_cache_file(tmp_path):
    """Use a temp directory for cache file isolation."""
    old_cache = BuildCache._cache.copy()
    BuildCache._cache = {}
    from nexy.builder import cache
    old_path = cache.CACHE_FILE
    cache.CACHE_FILE = tmp_path / "build.cache.json"
    yield tmp_path
    BuildCache._cache = old_cache
    cache.CACHE_FILE = old_path


def test_is_changed_returns_true_for_new_file(temp_cache_file):
    p = temp_cache_file / "test.nexy"
    p.write_text("---\n---\nHello")
    assert BuildCache.is_changed(p) is True


def test_is_changed_returns_false_after_mark(temp_cache_file):
    p = temp_cache_file / "test.nexy"
    p.write_text("---\n---\nHello")
    BuildCache.mark_built(p)
    assert BuildCache.is_changed(p) is False


def test_is_changed_returns_true_after_content_change(temp_cache_file):
    p = temp_cache_file / "test.nexy"
    p.write_text("---\n---\nHello")
    BuildCache.mark_built(p)
    p.write_text("---\n---\nWorld")
    assert BuildCache.is_changed(p) is True


def test_save_and_load_persists(temp_cache_file):
    from nexy.builder import cache
    p = temp_cache_file / "test.nexy"
    p.write_text("---\n---\nHello")
    BuildCache.mark_built(p)
    BuildCache.save()
    
    # Reload from file
    BuildCache._cache = {}
    BuildCache.load()
    assert BuildCache.is_changed(p) is False


def test_clear_removes_cache(temp_cache_file):
    p = temp_cache_file / "test.nexy"
    p.write_text("---\n---\nHello")
    BuildCache.mark_built(p)
    BuildCache.clear()
    assert BuildCache._cache == {}
```

## Verify commands

```bash
# Run the new cache tests
python -m pytest tests/unit/nexy/builder/test_cache.py -v

# Full test suite
python -m pytest tests/ -v
```

After verification:
- First `nx dev` — should compile all files (incremental=False)
- Edit one `.nexy` file in `src/` → only that file recompiled (check console output)
- `nx build` — should compile all files regardless of cache
- Delete `__nexy__/build.cache.json` — next build should recompile everything

## Definition of Done
- [ ] `BuildCache.is_changed()` returns True for new file, False after `mark_built()`
- [ ] `BuildCache.save()` + `load()` roundtrip preserves cache
- [ ] `BuildCache.clear()` empties cache
- [ ] `Builder.build(incremental=True)` skips unchanged files
- [ ] First `nx dev` compiles all files (full build, `incremental=False`)
- [ ] Subsequent saves only recompile changed files
- [ ] `nx build` always does full build + clears cache
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — all tests pass
