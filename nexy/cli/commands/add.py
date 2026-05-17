import typer
import subprocess
import shutil
import os
import urllib.request
from pathlib import Path
from typing import List, Optional
from nexy.utils.common.console import console
from nexy.utils.init.registry import COMPONENT_REGISTRY, ComponentEntry
from nexy.core.config import Config

def fetch_remote_component(url: str) -> Optional[str]:
    """Fetches component source from a remote URL."""
    try:
        with console.status(f"[yellow]nexy[/yellow] » Fetching remote component from {url}...", spinner="dots"):
            with urllib.request.urlopen(url) as response:
                return response.read().decode("utf-8")
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to fetch component from {url}: {e}")
        return None

def install_dependencies(deps: List[str]) -> None:
    """Installs node dependencies using the available package manager."""
    if not deps:
        return

    pnpm_lock = Path("pnpm-lock.yaml")
    yarn_lock = Path("yarn.lock")
    
    if pnpm_lock.exists() and shutil.which("pnpm"):
        cmd = ["pnpm", "add"]
    elif yarn_lock.exists() and shutil.which("yarn"):
        cmd = ["yarn", "add"]
    elif shutil.which("npm"):
        cmd = ["npm", "install"]
    else:
        console.print("[yellow]Warning:[/yellow] No package manager found. Please install dependencies manually: " + ", ".join(deps))
        return

    with console.status(f"[yellow]nexy[/yellow] » Installing dependencies: {', '.join(deps)}...", spinner="dots"):
        try:
            subprocess.run(
                cmd + deps, 
                check=True, 
                capture_output=True,
                shell=(os.name == "nt")
            )
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error:[/red] Failed to install dependencies: {e}")

def add(
    components: List[str] = typer.Argument(None, help="Components to add (registry names or URLs)"),
    ui: bool = typer.Option(False, "--ui", help="Force treatment as UI components"),
    url: bool = typer.Option(False, "--url", help="Force treatment as URLs"),
    all: bool = typer.Option(False, "--all", "-a", help="Add all available components from registry"),
) -> None:
    """
    Add components to your project as .nexy files.
    
    Example:
    nexy add button input
    nexy add --ui button input
    nexy add https://raw.githubusercontent.com/.../Button.tsx
    """
    config = Config()
    
    # Determine default target framework from config
    framework = "react"
    ff_list = getattr(config, "useFF", [])
    if ff_list:
        framework = ff_list[0].name.lower()

    if all:
        components = list(COMPONENT_REGISTRY.keys())
    
    if not components:
        console.print("[yellow]Usage:[/yellow] nexy add [COMPONENT_NAME or URL]...")
        console.print(f"Available UI components: [cyan]{', '.join(COMPONENT_REGISTRY.keys())}[/cyan]")
        raise typer.Exit()

    target_dir = Path("src/components/ui")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    all_deps = set()

    for item in components:
        content = None
        component_name = item
        framework_to_use = framework

        # Detection logic
        is_url = item.startswith(("http://", "https://")) or url
        
        if is_url:
            content = fetch_remote_component(item)
            if not content:
                continue
            
            url_path = Path(item)
            component_name = url_path.stem
            ext = url_path.suffix.lower()
            
            # Framework inference for URL
            if ext == ".vue": framework_to_use = "vue"
            elif ext == ".svelte": framework_to_use = "svelte"
            elif ext in (".tsx", ".jsx"): framework_to_use = "react"
            elif ext == ".solid": framework_to_use = "solid"
            elif ext == ".preact": framework_to_use = "preact"
            elif ext == ".nexy": framework_to_use = "nexy"
            else: framework_to_use = "react" # Default fallback
        
        else:
            name_lower = item.lower()
            if name_lower not in COMPONENT_REGISTRY:
                console.print(f"[red]Error:[/red] Component '[bold]{item}[/bold]' not found in registry.")
                continue
                
            entry = COMPONENT_REGISTRY[name_lower]
            component_name = entry.name
            
            if framework not in entry.framework_code:
                available = list(entry.framework_code.keys())
                framework_to_use = available[0]
            else:
                framework_to_use = framework
            
            content = entry.framework_code[framework_to_use]
            all_deps.update(entry.dependencies)

        _write_nexy_component(target_dir, component_name, content, framework_to_use)

    if all_deps:
        install_dependencies(list(all_deps))

def _write_nexy_component(target_dir: Path, name: str, content: str, framework: str) -> None:
    """Helper to write a .nexy file with optional framework wrapper."""
    file_path = target_dir / f"{name}.nexy"
    
    if file_path.exists():
        console.print(f"[yellow]Skipping:[/yellow] {file_path} already exists.")
        return

    # Wrap framework code in <script framework="..."> if it's not already a .nexy file
    if framework != "nexy" and not content.strip().startswith("<script"):
        final_content = f'<script framework="{framework}">\n{content}\n</script>'
    else:
        final_content = content

    try:
        file_path.write_text(final_content, encoding="utf-8")
        console.print(f"[green]Added:[/green] {file_path}")
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to write {file_path}: {e}")
        console.print("[green]✔[/green] All dependencies installed.")
