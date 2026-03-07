from __future__ import annotations
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request
import questionary
from nexy.__version__ import __Version__
from nexy.utils.console import console
from nexy.i18n import t

class InitProject:
    def __init__(self) -> None:
        self.version = __Version__().get()
        self.config = {}
        console.print(t("init.title", "nexy init").format(version=self.version))
        self.ask_router()
        self.ask_project_type()
    def check_nexy(): pass

    def ask_router(self) -> None:
        self.config['FBRouter'] = questionary.confirm(
            t("init.ask.router", "Use file-based router?"),
            default=True,
            qmark="»",
            instruction="(yes/no) "
        ).ask()

    def ask_project_type(self) -> None:
        # Vrai Select interactif
        choice = questionary.select(
            t("init.ask.project_type", "Choose the type of project"),
            choices=[
                questionary.Choice(t("init.choice.web", "Web (monolith web app)"), value="web"),
                questionary.Choice(t("init.choice.api", "API (RESTful API)"), value="api"),
            ],
            pointer="ʋ",
            qmark="»",
            show_description=True,
            show_selected=True,
        ).ask()
        if choice == "web":
            self.ask_client_component()

        self.config['project_type'] = choice


    def ask_client_component(self) -> None:
        use_client = questionary.confirm(t("init.ask.client_component", "Use a client component?"), default=True, qmark="»").ask()
        
        if use_client:
            framework = questionary.select(
                t("init.ask.framework", "Choose the client framework"),
                choices=["React", "Vue", "Svelte", "Preact", "None"],
                pointer="ʋ",
                qmark="»",
            ).ask()
            self.config['client_framework'] = framework
            self.ask_tailwindcss()


    def ask_tailwindcss(self) -> None:
        self.config['tailwind'] = questionary.confirm(t("init.ask.tailwind", "Use Tailwind CSS?"), default=True, qmark="»").ask()

    # --- Template Registry / Silent Clone ---
    def apply_template(self, template_name: Optional[str], registry_url: Optional[str]) -> None:
        url = registry_url or os.getenv("NEXY_TEMPLATE_REGISTRY", "").strip() or "https://registry.example.com/templates.json"
        try:
            templates = self._fetch_templates(url)
        except Exception as e:
            console.print(f"[yellow]nexy[/yellow] » " + t("init.registry_failed", "registry fetch failed: {error}. Using fallback list.").format(error=str(e)))
            templates = self._fallback_templates()

        entry: Optional[Dict[str, Any]] = None
        if template_name:
            entry = next((t for t in templates if t.get("name") == template_name or t.get("id") == template_name), None)
            if not entry:
                console.print(f"[red]nexy[/red] » template '{template_name}' not found in registry")
                return
        else:
            choices = [questionary.Choice(f"{t['name']} ({t.get('desc','')})", value=t['id']) for t in templates]
            chosen_id = questionary.select("Choose a template", choices=choices, pointer="ʋ", qmark="»").ask()
            entry = next((t for t in templates if t.get("id") == chosen_id), None)

        if not entry:
            console.print(f"[red]nexy[/red] » " + t("init.no_template", "no template selected"))
            return

        repo = entry.get("repo", "")
        branch = entry.get("branch", "main")
        dest = Path(".")
        dest_final = dest if self._is_empty_dir(dest) else Path(entry["name"])
        backed_up = False
        try:
            backed_up = self._stash_git_repo()
            self._git_clone(repo=repo, branch=branch, dest=dest_final)
            self._cleanup_git(dest_final)
        finally:
            if backed_up:
                self._restore_git_repo()
        console.print(f"[green]nexy[/green] » " + t("init.template_done", "template '{name}' initialized at {dest}").format(name=entry['name'], dest=dest_final.as_posix()))

    def _fetch_templates(self, url: str) -> List[Dict[str, Any]]:
        req = urllib.request.Request(url, headers={"User-Agent": "nexy-init"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return list(data) if isinstance(data, list) else []

    def _fallback_templates(self) -> List[Dict[str, Any]]:
        return [
            {"id": "react-web", "name": "react-web", "repo": "https://github.com/example/nexy-templates.git", "branch": "react-web", "desc": "React web app"},
            {"id": "vue-web", "name": "vue-web", "repo": "https://github.com/example/nexy-templates.git", "branch": "vue-web", "desc": "Vue web app"},
            {"id": "api-fastapi", "name": "api-fastapi", "repo": "https://github.com/example/nexy-templates.git", "branch": "api-fastapi", "desc": "FastAPI API server"},
        ]

    def _is_empty_dir(self, path: Path) -> bool:
        return not any(path.iterdir())

    def _git_clone(self, repo: str, branch: str, dest: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        cmd = ["git", "clone", "--depth=1", "--branch", branch, repo, dest.as_posix()]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"git clone failed: {proc.stderr.strip() or proc.stdout.strip()}")

    def _cleanup_git(self, dest: Path) -> None:
        gitdir = dest / ".git"
        if gitdir.exists():
            shutil.rmtree(gitdir, ignore_errors=True)

    def _stash_git_repo(self) -> bool:
        root = Path(".")
        gitdir = root / ".git"
        backup = root / ".git_old"
        if gitdir.exists():
            if backup.exists():
                shutil.rmtree(backup, ignore_errors=True)
            try:
                gitdir.rename(backup)
                return True
            except Exception:
                return False
        return False

    def _restore_git_repo(self) -> None:
        root = Path(".")
        gitdir = root / ".git"
        backup = root / ".git_old"
        if backup.exists():
            if gitdir.exists():
                shutil.rmtree(gitdir, ignore_errors=True)
            try:
                backup.rename(gitdir)
            except Exception:
                # En dernier recours, recopier le dossier
                shutil.copytree(backup, gitdir, dirs_exist_ok=True)
                shutil.rmtree(backup, ignore_errors=True)
