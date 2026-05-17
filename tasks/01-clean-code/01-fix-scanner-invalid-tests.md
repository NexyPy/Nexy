# Task 01: Fix invalid scanner tests

## Goal
Make `test_scanner_invalid_1` through `test_scanner_invalid_4` pass — they currently fail because `Scanner.scan()` never raises `ValueError`.

## TDD (RED → GREEN → REFACTOR)

### RED (tests exist, they fail)
Run `python -m pytest tests/unit/nexy/parser/test_scanner.py -v`
Observe: `test_scanner_invalid_1..4` all raise `Failed: DID NOT RAISE <class 'ValueError'>`

### GREEN — modify `nexy/compiler/parser/scanner.py`
Add validation to `scan()` method:
- If source has no `---` delimiter → raise `ValueError("Missing '---' delimiter")`
- If source has opening `---` but no closing `---` → raise `ValueError("Unclosed '---' delimiter")`
- If source is empty or only delimiters → raise `ValueError("Empty .nexy file")`

The regex pattern `^\s*---\s*(?P<logic>.*?)\s*---\s*(?P<template>.*)` with `re.DOTALL` already exists. Add explicit checks before/after matching.

### REFACTOR
- Keep `_PATTERN` as compiled regex
- Add a single validation method `_validate(source: str, match: re.Match | None)` that raises specific errors

## Definition of done
- [ ] All 4 `test_scanner_invalid_*` pass
- [ ] All existing valid scanner tests still pass
- [ ] No new functions added outside `Scanner` class
