from dataclasses import dataclass, field

from nexy.builder.discovery import Discovery
from nexy.compiler import Compiler
from nexy.core.config import Config
from nexy.utils.common.console import console


@dataclass
class BuildResult:
    success: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)


class Builder:
    def __init__(self) -> None:
        self.discovery = Discovery()
        self.compiler = Compiler()
        self.config = Config()

        exclude_dirs = self.config.excludeDirs
        for name in exclude_dirs:
            self.discovery.add_excluded_dir(name)

    def build(self, showlog: bool = False) -> BuildResult:
        files = self.discovery.scan(self.config.PROJECT_ROOT)
        result = BuildResult()
        for file in files:
            input_path = file.as_posix()
            try:
                self.compiler.compile(input=input_path)
                result.success.append(input_path)
                if showlog:
                    console.print(
                        f"[green]nsc[/green] » compiled [reset][dim]{input_path}[/dim]"
                    )
            except Exception as e:
                result.failed.append(input_path)
                msg = f"error compiling {input_path}: {e}"
                console.print(f"[red]nsc[/red] » {msg}")
                if showlog:
                    import traceback as _tb
                    _tb.print_exc()
        return result


__all__ = ["Builder"]
