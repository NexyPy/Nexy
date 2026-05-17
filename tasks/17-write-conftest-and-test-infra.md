# Task 17: Create shared test infrastructure (conftest.py)

## Goal
Provide shared fixtures so tests are DRY and reusable.

## Step 1: Create `tests/conftest.py`

```python
import pytest
from pathlib import Path


@pytest.fixture
def sample_nexy_file(tmp_path: Path) -> Path:
    """Creates a temporary .nexy file with basic frontmatter + template."""
    p = tmp_path / "test.nexy"
    p.write_text("---\ntitle: prop[str] = \"Hello\"\n---\n<h1>{{ title }}</h1>", encoding="utf-8")
    return p


@pytest.fixture
def sample_mdx_file(tmp_path: Path) -> Path:
    """Creates a temporary .mdx file with frontmatter."""
    p = tmp_path / "test.mdx"
    p.write_text("---\ntitle: prop[str]\n---\n# {{ title }}", encoding="utf-8")
    return p


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Creates a temp project with src/routes/ and nexyconfig.py."""
    routes = tmp_path / "src" / "routes"
    routes.mkdir(parents=True)
    (tmp_path / "nexyconfig.py").write_text(
        "from nexy.core.models import NexyConfigModel\n"
        "class NexyConfig(NexyConfigModel): pass\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def temp_nexy_file_in_project(temp_project: Path) -> Path:
    """Creates a .nexy file inside a temp project's src/routes/."""
    p = temp_project / "src" / "routes" / "index.nexy"
    p.write_text("---\ntitle: prop[str] = \"Home\"\n---\n<h1>{{ title }}</h1>", encoding="utf-8")
    return p
```

## Step 2: Verify conftest is discovered

```bash
# pytest should discover and use conftest fixtures
python -m pytest tests/ --collect-only 2>&1 | Select-String -Pattern "sample_nexy_file|temp_project"
```

## Step 3: Update `pyproject.toml` test config

Ensure this section exists (it likely already does):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

## Verify commands

```bash
# Fixtures work
python -c "
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
sys.path.insert(0, 'tests')
# Just check the conftest can be imported
"

python -m pytest tests/ -v --setup-show 2>&1 | Select-String -Pattern "fixture" | Select-Object -First 10
```

## Definition of Done
- [ ] `tests/conftest.py` created with reusable fixtures (`sample_nexy_file`, `sample_mdx_file`, `temp_project`)
- [ ] Existing tests still pass (`python -m pytest tests/ -v`)
- [ ] New tests can use `sample_nexy_file` and `temp_project` fixtures directly
