from pathlib import Path
import shutil
import subprocess
import os
import stat
from typing import Any, Callable

from nexy.cli.commands.utilities.console import console
from nexy.i18n import t


class GitClone:

    def __init__(self) -> None:
        self.repo = "https://github.com/NexyPy/nexy.git"
        self.branch = "master" # Templates are in the master branch of the nexy repo
        self.dest = Path(".")
        self.is_windows = os.name == "nt"

    def _is_empty_dir(self, path: Path) -> bool:
        return not any(path.iterdir())
    
    def clone(self, repo: str, branch: str, dest: Path, subdir: str | None = None) -> None:
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
                    subprocess.run(
                        cmd, 
                        cwd=dest.as_posix(), 
                        capture_output=True, 
                        text=True, 
                        check=True,
                        shell=self.is_windows
                    )
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
                    subprocess.run(
                        checkout_cmd, 
                        cwd=dest.as_posix(), 
                        capture_output=True, 
                        text=True, 
                        check=True,
                        shell=self.is_windows
                    )
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
                        subprocess.run(
                            cmd, 
                            cwd=dest.as_posix(), 
                            capture_output=True, 
                            text=True, 
                            check=True,
                            shell=self.is_windows
                        )
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
            
        excluded = ["build", "dist", ".venv", "node_modules", "__pycache__"]
            
        for item in source.iterdir():
            if item.name in excluded:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink()
                continue
                
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

    def _cleanup_git(self, dest: Path) -> None:

        """Removes the .git directory to cut any link with the remote repository."""

        def on_rm_error(func: Callable[[str], Any], path: str, exc_info: tuple[object, ...]) -> None:
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
            def on_rm_error(func: Callable[[str], Any], path: str, exc_info: tuple[object, ...]) -> None:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            shutil.rmtree(backup, onerror=on_rm_error)

        if gitdir.exists():
            try:
                gitdir.rename(backup)
                return True
            except Exception:
                try:
                    shutil.copytree(gitdir, backup, dirs_exist_ok=True)
                    def on_rm_error(func: Callable[[str], Any], path: str, exc_info: tuple[object, ...]) -> None:
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
                def on_rm_error(func: Callable[[str], Any], path: str, exc_info: tuple[object, ...]) -> None:
                    os.chmod(path, stat.S_IWRITE)
                    func(path)

                try:
                    shutil.copytree(backup, gitdir, dirs_exist_ok=True)
                    shutil.rmtree(backup, onerror=on_rm_error)
                except Exception:
                    pass
