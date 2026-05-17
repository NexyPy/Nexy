import os
from pathlib import Path

from nexy.core.models import ParserModel
from nexy.errors import NexyCompileError
from nexy.utils.common.console import console
from nexy.utils.fs.vfs import VFS

from .logic import LogicGenerator
from .template import TemplateGenerator


class Generator:
    def __init__(self) -> None:
        self.output: str = ""
        self.source: ParserModel | None = None
        self.template = TemplateGenerator()
        self.logic = LogicGenerator()
        self.vfs = VFS()

    def generate(self, output: str, source: ParserModel, source_path: str = None) -> bool:
        self.source = source
        try:
            directory = os.path.dirname(output)
            # No need to create physical directories in development
            # unless we are in production build mode
            # For now, we just write to VFS
            self.logic.generate(template_path=output, source=self.source, source_path=source_path)
            self.template.generate(output=output, source=self.source.template)
            self._generate_init(directory)
            return True
        except Exception as e:
            console.print(f"[red]nsc[/red] » Error writing to file '{output}': {e}")
            raise NexyCompileError(source_path=output, message=str(e))

    def _generate_init(self, directory: str) -> None:
        parts = directory.replace("\\", "/").split("/")
        for i in range(1, len(parts) + 1):
            sub = "/".join(parts[:i])
            init_file = f"{sub}/__init__.py"
            if not self.vfs.exists(init_file):
                self.vfs.write(init_file, "")


__all__ = ["Generator"]
