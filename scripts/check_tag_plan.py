import re
import sys
from pathlib import Path

README = Path("README.md")

SECTION_TITLE = re.compile(r"^#+\s*Release Tag Planning", re.IGNORECASE)
TABLE_HEADER = re.compile(r"^\|\s*Version\s*\|\s*Target Date\s*\|\s*Status\s*\|", re.IGNORECASE)

def main() -> int:
    if not README.exists():
        print("README.md not found", file=sys.stderr)
        return 1
    lines = README.read_text(encoding="utf-8").splitlines()
    has_section = any(SECTION_TITLE.search(l) for l in lines)
    if not has_section:
        print("Missing 'Release Tag Planning' section in README.md", file=sys.stderr)
        return 1
    # Look for a table header under the section
    in_section = False
    has_table = False
    for line in lines:
        if SECTION_TITLE.search(line):
            in_section = True
            continue
        if in_section:
            if TABLE_HEADER.search(line):
                has_table = True
                break
            if line.strip().startswith("#"):
                break
    if not has_table:
        print("Missing release planning table (Version/Target Date/Status) in README.md", file=sys.stderr)
        return 1
    print("README release tag planning found ✓")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

