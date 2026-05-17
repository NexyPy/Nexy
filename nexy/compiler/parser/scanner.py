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
        source_content = (source or "").strip()

        # 1. Empty file check
        if not source_content:
            return ScanResult(logic_block="", template_block="")

        # 2. Check for delimiters
        if "---" not in source_content:
            # No delimiters: everything is template
            return ScanResult(
                logic_block="",
                template_block=source_content,
            )

        # 3. Handle delimiters
        parts = source_content.split("---")

        # If there's only one "---", it's invalid (unclosed or just a separator)
        if len(parts) < 3:
            # If "---" is present but not as a pair at the start,
            # check if it's just content. Nexy philosophy: frontmatter MUST be at the very top.
            if source_content.startswith("---"):
                raise ValueError("Unclosed '---' delimiter")
            else:
                # If "---" is in the middle but doesn't start with it, treat as template
                return ScanResult(
                    logic_block="",
                    template_block=source_content,
                )

        match = self._PATTERN.match(source_content)

        if match:
            logic = match.group("logic").strip()
            template = match.group("template").strip()
            return ScanResult(
                logic_block=logic,
                template_block=template,
            )

        # 4. If it starts with --- but doesn't match the pattern (content before ---)
        if source_content.startswith("---"):
            raise ValueError("Malformed .nexy file: content found before opening '---' delimiter")

        # Default: treat as template
        return ScanResult(
            logic_block="",
            template_block=source_content,
        )

    def process(self, source: str) -> ScanResult:
        return self.scan(source)
