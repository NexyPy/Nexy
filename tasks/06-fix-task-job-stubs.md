# Task 06: Fix `Task` and `Job` stubs — replace with `NotImplementedError`

## Problem
`nexy/decorators.py:338-339`:
```python
def Task(func: Optional[Callable] = None): pass
def Job(func: Optional[Callable] = None): pass
```

These are no-op stubs. `pass` returns `None`. If a user writes:
```python
@Task
def my_task():
    ...
```
The function `my_task` is replaced with `None`. `my_task()` raises `TypeError: 'NoneType' object is not callable`.

## Step 1: Read the file
```bash
Get-Content -LiteralPath "nexy/decorators.py" | Select-Object -Last 20
```

Find lines around 338-339.

## Step 2: Replace the old stubs

Use `edit` tool:

**oldString:**
```python
def Task(func: Optional[Callable] = None): pass
def Job(func: Optional[Callable] = None): pass
```

**newString:**
```python
def Task(func: Optional[Callable] = None) -> Callable:
    raise NotImplementedError("Scheduled tasks (@Task) are not yet implemented in Nexy")

def Job(func: Optional[Callable] = None) -> Callable:
    raise NotImplementedError("Scheduled jobs (@Job) are not yet implemented in Nexy")
```

## Step 3: Test the fix
```bash
python -c "from nexy import Task; Task(lambda: None)"
# Should raise: NotImplementedError: Scheduled tasks (@Task) are not yet implemented in Nexy
```

## Verify commands
```bash
ruff check nexy/decorators.py
python -m mypy nexy/decorators.py --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] `Task()` raises `NotImplementedError` with descriptive message
- [ ] `Job()` raises `NotImplementedError` with descriptive message
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
