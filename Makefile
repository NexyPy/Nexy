PY ?= python

.PHONY: help lint typecheck test perf py.lint py.typecheck py.test ts.lint ts.typecheck

help:
	@echo "Targets:"
	@echo "  lint          Run Python and TS linters"
	@echo "  typecheck     Run mypy and TS type checks"
	@echo "  test          Run pytest and (if configured) extension tests"
	@echo "  perf          Run performance benchmarks (fail on >5% regression)"

lint: py.lint ts.lint

typecheck: py.typecheck ts.typecheck

test: py.test

py.lint:
	@echo ">> Ruff lint"
	@ruff check nexy || exit 1

py.typecheck:
	@echo ">> mypy"
	@mypy nexy || exit 1

py.test:
	@echo ">> pytest"
	@pytest -q --maxfail=1 --disable-warnings || exit 1

ts.lint:
	@echo ">> eslint (extensions/vscode)"
	@npm --prefix extensions/vscode run lint || exit 0

ts.typecheck:
	@echo ">> tsc (extensions/vscode)"
	@npm --prefix extensions/vscode run check-types || exit 0

perf:
	@$(PY) scripts/perf.py check

docs.check:
	@$(PY) scripts/check_tag_plan.py
