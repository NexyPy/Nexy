import json
import subprocess
import sys
import time
from pathlib import Path

from nexy.__version__ import __Version__
from nexy.builder import Builder
from nexy.core.config import Config
from nexy.frontend import FrontendGenerator
from nexy.utils.common.console import console
from nexy.utils.server.server import Server


def build(check: bool = False) -> None:
    build_start = time.perf_counter()
    config = Config()
    version = __Version__().get()
    Server.check_nexy_prod()
    console.print(f"nexy@{version} build\n")
    console.print("Creating an optimized production build\n")

    with console.status("  compiling server components ..."):
        from nexy.utils.fs.vfs import VFS

        FrontendGenerator().generate(ssg=True)
        build_result = Builder().build(showlog=False)
        VFS().flush_to_disk()
    server_ko = len(build_result.failed)
    if server_ko:
        console.print(f"  [red]✘[/red] {server_ko} component(s) failed")
        for p in build_result.failed:
            console.print(f"     {p}")
        sys.exit(1)

    ssg_entries: list[dict] = []
    if config.useVite:
        with console.status("  building client bundle ..."):
            vite_proc = Server.vite(build=True, suppress_output=True)
            _, err = vite_proc.communicate()
            if vite_proc.returncode != 0:
                console.print("  [red]✘[/red] client build failed")
                if err:
                    console.print(f"[red]{err.decode()}[/red]")
                sys.exit(1)

            report_path = Path("__nexy__/client/ssg-report.json")
            if report_path.exists():
                ssg_entries = json.loads(report_path.read_text())

    if check:
        _run_checks()

    _show_summary(build_result, ssg_entries)

    build_elapsed = time.perf_counter() - build_start
    console.print(f"\n  [green]✓[/green] build in [bold]{build_elapsed:.2f}s[/bold]")


def _show_summary(build_result, ssg_entries: list[dict]) -> None:
    _print_section("server components", build_result.success, build_result.failed, "green", "red")
    _print_section(
        "client components",
        _ssg_success(ssg_entries),
        _ssg_failed(ssg_entries),
        "cyan",
        "red",
        _ssg_skip(ssg_entries),
    )


def _ssg_success(entries: list[dict]) -> list[str]:
    return [e["file"] for e in entries if e["status"] == "success"]


def _ssg_failed(entries: list[dict]) -> list[str]:
    return [e["file"] for e in entries if e["status"] == "failed"]


def _ssg_skip(entries: list[dict]) -> list[str]:
    return [e["file"] for e in entries if e["status"] == "not_supported"]


def _print_section(
    title: str,
    success: list[str],
    failed: list[str],
    ok_style: str,
    fail_style: str,
    skipped: list[str] | None = None,
) -> None:
    total = len(success) + len(failed) + (len(skipped) if skipped else 0)
    console.print(f"\n{title} [{total}]")
    console.print("[dim]\u2502[/dim]")

    groups: list[tuple[str, list[str], str, str]] = [
        ("Build success", success, ok_style, "\u2713"),
        ("Build Failed", failed, fail_style, "\u2717"),
    ]
    for gi, (gname, gfiles, gstyle, mark) in enumerate(groups):
        is_last_group = gi == len(groups) - 1
        gprefix = "\u2514\u2500\u2500" if is_last_group else "\u251c\u2500\u2500"
        console.print(f"[dim]{gprefix} {gname} [{len(gfiles)}][/dim]")

        shown = gfiles[:3]
        has_more = len(gfiles) > 3

        for fi, f in enumerate(shown):
            is_last_item = fi == len(shown) - 1 and not has_more
            stem = "\u2514\u2500\u2500" if is_last_item else "\u251c\u2500\u2500"
            fprefix = f"\u2502   {stem}"
            sz = _file_size(f)
            sz_display = f"  [{sz}]" if sz else ""
            console.print(f"[dim]{fprefix} {fi + 1}. {f}{sz_display}[/dim] [{gstyle}]{mark}[/]")

        if has_more:
            more = len(gfiles) - 3
            console.print(f"[dim]\u2502   \u2514\u2500\u2500 [{more} more][/dim]")

        if not is_last_group:
            console.print("[dim]\u2502[/dim]")


def _file_size(filepath: str) -> str:
    base = Path(filepath)
    html_path = Path("__nexy__/client/static") / base.parent / f"{base.stem}.Default.html"
    if html_path.exists():
        return _fmt_size(html_path.stat().st_size)
    if base.exists():
        return _fmt_size(base.stat().st_size)
    return ""


def _fmt_size(b: int) -> str:
    if b < 1024:
        return f"{b}B"
    if b < 1024 * 1024:
        return f"{b / 1024:.1f}kB"
    return f"{b / (1024 * 1024):.1f}MB"


def _run_checks() -> None:
    console.print()
    checks = [
        ("ruff check", ["ruff", "check", "."]),
        ("ruff format", ["ruff", "format", ".", "--check"]),
        ("mypy", [sys.executable, "-m", "mypy", "."]),
    ]
    failed = False
    for name, cmd in checks:
        with console.status(f"  {name} ..."):
            r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            console.print(f"  [green]✓[/green] {name}")
        else:
            console.print(f"  [red]✘[/red] {name}")
            if r.stdout:
                console.print(r.stdout)
            if r.stderr:
                console.print(f"[red]{r.stderr}[/red]")
            failed = True
    if failed:
        console.print("\n  [red]checks failed[/red]")
        sys.exit(1)
    console.print("\n  [green]✓[/green] all checks passed")
