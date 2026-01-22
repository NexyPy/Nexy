from dataclasses import dataclass


@dataclass
class ScanResult:
    logic_block: str
    template_block: str

    @property
    def frontmatter(self) -> str:
        return self.logic_block

    @property
    def template(self) -> str:
        return self.template_block