import re
from nexy.core.models import ScanResult

class Scanner:
    """
    Separates Python logic from HTML/Jinja template.
    Logic is only extracted if enclosed by two '---' markers.
    """

    # Strictly matches: ^ --- logic --- template
    _PATTERN = re.compile(
        r"^\s*---\s*(?P<logic>.*?)\s*---\s*(?P<template>.*)",
        re.DOTALL,
    )

    def scan(self, source: str) -> ScanResult:
        source_content = source or ""
        match = self._PATTERN.match(source_content)

        if match:
            # Full structure found
            return ScanResult(
                logic_block=match.group("logic").strip(),
                template_block=match.group("template").strip(),
            )

        # No markers or unclosed block: treat everything as template
        return ScanResult(
            logic_block="",
            template_block=source_content.strip(),
        )

    def process(self, source: str) -> ScanResult:
        return self.scan(source)