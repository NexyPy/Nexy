from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
import questionary
from nexy.__version__ import __Version__
from nexy.utils.console import console
from nexy.i18n import t

BRANCH_MODEL = "[router]-[project_type]-[client_framework]"
WEB_APP = {
    "fbr-react":"",
    "modular-react":"",

    "fbr-vue":"",
    "modular-vue":"",

    "fbr-preact":"",
    "modular-preact":"",

    "fbr-svelte":"",
    "modular-svelte":"",
    "fbr-none":"",
    "modular-none":"",
}

WEB_API = {
    "modular":"",
    "fbr":""
}

class InitProject:
    def __init__(self) -> None:
        self.version = __Version__().get()
        self.config = {}

    def ask_questions(self) -> None:
        """Triggers the interactive questions to collect configuration."""
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

   
    def _is_empty_dir(self, path: Path) -> bool:
        return not any(path.iterdir())

    def _git_clone(self, repo: str, branch: str, dest: Path, subdir: str | None = None) -> None:
        """Clones the template. If subdir is provided, extracts only that directory's contents."""
        # On sauvegarde le dépôt git de l'utilisateur s'il existe déjà
        has_user_git = self._stash_git_repo()
        
        try:
            # Si le dossier contient seulement .venv ou est vide, on peut cloner/extraire
            is_empty = self._is_empty_dir(dest)
            has_only_venv = False
            if not is_empty:
                items = [i for i in dest.iterdir() if i.name != ".git_old"]
                if len(items) == 0:
                    is_empty = True
                elif len(items) == 1 and items[0].name == ".venv":
                    has_only_venv = True

            # Common init steps
            init_cmds = [
                ["git", "init"],
                ["git", "remote", "add", "origin", repo],
                ["git", "fetch", "--depth=1", "origin", branch],
            ]
            for cmd in init_cmds:
                try:
                    subprocess.run(cmd, cwd=dest.as_posix(), capture_output=True, text=True, check=True)
                except subprocess.CalledProcessError as e:
                    if "fetch" in cmd and e.returncode == 128:
                        raise Exception(t("init.template_not_found", "Template or branch '{branch}' not found on remote.").format(branch=branch))
                    raise e

            # Extraction logic (sparse or merge)
            checkout_path = subdir if subdir else "."
            
            if is_empty or has_only_venv:
                # Checkout the subdir contents to the root
                checkout_cmd = ["git", "checkout", "FETCH_HEAD", "--", checkout_path]
                try:
                    subprocess.run(checkout_cmd, cwd=dest.as_posix(), capture_output=True, text=True, check=True)
                except subprocess.CalledProcessError:
                    raise Exception(t("init.checkout_failed", "Failed to extract files from template '{path}'.").format(path=checkout_path))
                
                # If we used a subdir, move files to root and cleanup
                if subdir:
                    self._move_subdir_to_root(dest, Path(subdir))
            else:
                console.print(f"[yellow]nexy[/yellow] » " + t("init.merging", "Directory not empty, merging files..."))
                # Standard merge approach
                merge_cmds = [
                    ["git", "checkout", "FETCH_HEAD", "--", checkout_path],
                    ["git", "merge", "--ff-only", "FETCH_HEAD"],
                    ["git", "reset", "--hard"]
                ]
                for cmd in merge_cmds:
                    try:
                        subprocess.run(cmd, cwd=dest.as_posix(), capture_output=True, text=True, check=True)
                    except subprocess.CalledProcessError:
                        raise Exception(t("init.checkout_failed", "Failed to extract files from template '{path}'.").format(path=checkout_path))
                
                if subdir:
                    self._move_subdir_to_root(dest, Path(subdir))
        
        finally:
            # Suppression radicale du dossier .git du template pour couper tout lien (origin)
            self._cleanup_git(dest)
            
            # Restauration du dépôt git de l'utilisateur s'il existait
            if has_user_git:
                self._restore_git_repo()

    def _move_subdir_to_root(self, root: Path, subdir: Path) -> None:
        """Moves all contents from a subdirectory to the root and removes the subdirectory."""
        source = root / subdir
        if not source.exists():
            return
            
        for item in source.iterdir():
            target = root / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target, ignore_errors=True)
                else:
                    target.unlink()
            shutil.move(str(item), str(root))
            
        # Remove empty parent dirs of the subdir
        current = source
        while current != root:
            parent = current.parent
            shutil.rmtree(current, ignore_errors=True)
            current = parent
            if any(current.iterdir()):
                break

    def resolve_template_path(self) -> str:
        """Resolves the template folder path based on the user's choices."""
        router = "fbr" if self.config.get('FBRouter') else "modular"
        project_type = self.config.get('project_type', 'web')
        client_framework = self.config.get('client_framework', 'none').lower()
        
        # Structure: templates/[project_type]-[router]-[client_framework]
        if project_type == "api":
            return f"templates/api-{router}"
        
        return f"templates/{project_type}-{router}-{client_framework}"

    def install_dependencies(self, dest: Path) -> None:
        """Installs dependencies using uv (Python) and detected JS manager (bun/pnpm/npm)."""
        # Python dependencies with uv
        console.print(f"[blue]nexy[/blue] » " + t("init.deps.installing_python", "Installing Python dependencies with uv..."))
        try:
            # Check if uv is installed
            subprocess.run(["uv", "--version"], capture_output=True, check=True)
            
            # Use uv sync if pyproject.toml exists, else uv pip install
            if (dest / "pyproject.toml").exists():
                subprocess.run(["uv", "sync"], cwd=dest.as_posix(), check=True)
            elif (dest / "requirements.txt").exists():
                subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], cwd=dest.as_posix(), check=True)
            
            console.print(f"[green]nexy[/green] » " + t("init.deps.python_installed", "Python dependencies installed successfully."))
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print(f"[yellow]nexy[/yellow] » " + t("init.deps.uv_not_found", "uv not found, falling back to pip..."))
            # Fallback to pip if uv is not available
            pip_path = dest / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / "pip"
            pip_cmd = pip_path.as_posix() if pip_path.exists() else "pip"
            if (dest / "requirements.txt").exists():
                subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], cwd=dest.as_posix(), check=True)

        # JS dependencies if package.json and vite.config.ts exist
        if (dest / "package.json").exists() and (dest / "vite.config.ts").exists():
            console.print(f"[blue]nexy[/blue] » " + t("init.deps.installing_js", "Installing JS dependencies..."))
            
            # Detect manager: bun > pnpm > npm
            js_manager = "npm"
            for manager in ["bun", "pnpm"]:
                try:
                    subprocess.run([manager, "--version"], capture_output=True, check=True)
                    js_manager = manager
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            try:
                console.print(f"[blue]nexy[/blue] » " + t("init.deps.using_manager", "Using {manager}...").format(manager=js_manager))
                subprocess.run([js_manager, "install"], cwd=dest.as_posix(), check=True)
                console.print(f"[green]nexy[/green] » " + t("init.deps.js_installed", "JS dependencies installed successfully."))
            except subprocess.CalledProcessError as e:
                console.print(f"[red]nexy[/red] » " + t("init.deps.js_error", "Error installing JS dependencies: {error}").format(error=e))

    def run(self, template: str | None = None) -> None:
        """Executes the full initialization process."""
        if template is None:
            if not self.config:
                self.ask_questions()
            template_path = self.resolve_template_path()
        else:
            # Map user-friendly name (e.g., web-fbr-react) to folder path (templates/web-fbr-react)
            # Ensure it always starts with templates/ folder in the remote repo
            template_path = f"templates/{template}"
        
        # In dev mode (if we are in the nexy repo), we might want to use local templates
        is_dev = (Path(__file__).parents[3] / "templates").exists()
        
        if is_dev:
            local_templates = Path(__file__).parents[3] / template_path
            if local_templates.exists():
                console.print(f"[blue]nexy[/blue] » Using local template: {template_path}")
                dest = Path(".")
                # Simple copy instead of git clone
                shutil.copytree(local_templates, dest, dirs_exist_ok=True)
                self.install_dependencies(dest)
                console.print(f"\n[green]nexy[/green] » " + t("init.success", "Project initialized successfully!"))
                return

        repo = "https://github.com/NexyPy/nexy.git"
        branch = "master" # Templates are in the master branch of the nexy repo
        dest = Path(".")
        
        try:
            # The template parameter is now used as a subdir
            # We strictly extract ONLY from the templates/ directory
            self._git_clone(repo, branch, dest, subdir=template_path)
            self.install_dependencies(dest)
            
            console.print(f"\n[green]nexy[/green] » " + t("init.success", "Project initialized successfully!"))
            console.print(f"[bold]{t('init.next_steps', 'Next steps:')}[/bold]")
            console.print(f"  1. [cyan]nexy dev[/cyan]")
        except Exception as e:
            console.print(f"[red]nexy[/red] » {t('init.failed', 'Initialization failed: {error}').format(error=e)}")

    def _cleanup_git(self, dest: Path) -> None:
        """Removes the .git directory to cut any link with the remote repository."""
        import os
        import stat

        def on_rm_error(func, path, exc_info):
            # Clear read-only bit and retry
            os.chmod(path, stat.S_IWRITE)
            func(path)

        gitdir = dest / ".git"
        if gitdir.exists():
            shutil.rmtree(gitdir, onerror=on_rm_error)
        
        # Supprime également .github si présent (souvent spécifique au dépôt du template)
        githubdir = dest / ".github"
        if githubdir.exists():
            shutil.rmtree(githubdir, onerror=on_rm_error)

    def _stash_git_repo(self) -> bool:
        """Backs up the existing .git directory to .git_old."""
        root = Path(".")
        gitdir = root / ".git"
        backup = root / ".git_old"
        
        # If backup already exists, we must remove it first to avoid rename errors
        if backup.exists():
            import os
            import stat
            def on_rm_error(func, path, exc_info):
                os.chmod(path, stat.S_IWRITE)
                func(path)
            shutil.rmtree(backup, onerror=on_rm_error)

        if gitdir.exists():
            try:
                gitdir.rename(backup)
                return True
            except Exception:
                # If rename fails, try copy and delete
                try:
                    shutil.copytree(gitdir, backup, dirs_exist_ok=True)
                    import os
                    import stat
                    def on_rm_error(func, path, exc_info):
                        os.chmod(path, stat.S_IWRITE)
                        func(path)
                    shutil.rmtree(gitdir, onerror=on_rm_error)
                    return True
                except Exception:
                    return False
        return False

    def _restore_git_repo(self) -> None:
        """Restores the .git directory from .git_old and deletes the backup."""
        root = Path(".")
        gitdir = root / ".git"
        backup = root / ".git_old"
        
        if backup.exists():
            # If a new .git was created by the template extraction, remove it
            if gitdir.exists():
                self._cleanup_git(root)
            
            try:
                # Restore by renaming (effectively deletes backup)
                backup.rename(gitdir)
            except Exception:
                # Fallback to copy and delete
                import os
                import stat
                def on_rm_error(func, path, exc_info):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                
                try:
                    shutil.copytree(backup, gitdir, dirs_exist_ok=True)
                    shutil.rmtree(backup, onerror=on_rm_error)
                except Exception:
                    pass
