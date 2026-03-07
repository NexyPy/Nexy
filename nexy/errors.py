from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class NexyCompileError(Exception):
    source_path: str
    message: str
    line: Optional[int] = None
    column: Optional[int] = None

    def __str__(self) -> str:
        loc = ""
        if self.line is not None:
            col = self.column if self.column is not None else 0
            loc = f":{self.line}:{col}"
        return f"{self.source_path}{loc} - {self.message}"

