from nexy.builder.discovery import Discovery
from nexy.utils.console import console
from nexy.compiler import Compiler
from nexy.core.config import Config


class Builder:
    def __init__(self) -> None:
        self.discovery = Discovery()
        self.compiler = Compiler()
        self.config = Config()

        exclude_dirs = getattr(self.config, "excludeDirs", [])
        for name in exclude_dirs:
            self.discovery.add_excluded_dir(name)

    def build(self,showlog: bool = False) -> None:
        files = self.discovery.scan(self.config.PROJECT_ROOT)
        for file in files:
            input_path = file.as_posix()
            try:
                self.compiler.compile(input=input_path)
                if showlog:
                    console.print(f"[green]nsc[/green] » compiled [reset][dim]{input_path}[/dim] [green]✓[/green]")
            except Exception as e:
                console.print(f"[red]nsc[/red] » error compiling [reset][dim]{input_path}[/dim] [red]✗[/red]")
                console.print(f"[red]nsc[/red] » {e}")

__all__ = ["Builder"]
