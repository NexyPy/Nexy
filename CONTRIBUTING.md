Contributing to Nexy

Development Setup

1. Python 3.12+ and Node.js 20+
2. Install Python deps:

   pip install -e .[dev]

3. VS Code extension (optional):

   cd extensions/vscode && npm i

Workflow

- Branches: feature/*, fix/*, docs/*, perf/*
- Commits: Conventional Commits (feat:, fix:, docs:, refactor:, perf:, test:, chore:)
- PRs: one module/feature per PR, include tests and perf notes

Code Style

- Python: Ruff, mypy (strict), pytest, Google-style docstrings
- TypeScript: ESLint, tsc --noEmit
- i18n: English by default; extract strings to i18n/en.json

Quality Gates

- make lint, make typecheck, make test must pass
- make perf must not regress > 5%

Testing

- Python: pytest (≥95% module coverage target)
- TS extension: add tests under extensions/vscode/src/test

Releasing

- Update CHANGELOG, bump version, tag, publish

