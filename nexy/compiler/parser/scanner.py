import re
from nexy.core.models import ScanResult
class Scanner:
    _PATTERN = re.compile(
        r"^\s*---\s*(?P<frontmatter>.*?)\s*---\s*(?P<template>.*)",
        re.DOTALL,
    )

    def scan(self, source: str) -> ScanResult:
        match = self._PATTERN.match(source)

        if match is None:
            raise ValueError("Nexy format error: Frontmatter delimiters '---' are missing")

        return ScanResult(
            logic_block=match.group("frontmatter").strip(),
            template_block=match.group("template").strip(),
        )

    def process(self, source: str) -> ScanResult:
        return self.scan(source)