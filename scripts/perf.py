import json
import os
import subprocess
import sys
import time
from pathlib import Path

BASELINE_PATH = Path("docs/perf/baseline.json")
RESULTS_PATH = Path("docs/perf/latest.json")


def measure_cli_cold_start() -> float:
    t0 = time.perf_counter()
    # Spawn a fresh interpreter to simulate cold start import of CLI
    proc = subprocess.run(
        [sys.executable, "-c", "import nexy.cli; print('ok')"],
        capture_output=True,
        text=True,
        check=False,
    )
    t1 = time.perf_counter()
    return (t1 - t0) * 1000.0


def measure_template_generation() -> float:
    # Placeholder synthetic benchmark: import core modules used by generation
    t0 = time.perf_counter()
    code = (
        "from nexy.compiler import Compiler; "
        "c=Compiler(); "
        "import io; "
        "src='---\\n\\n---\\n<h1>Hello</h1>'; "
        "c.compile(input='src/routes/index.nexy', output='__nexy__/tmp/index.html')"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    t1 = time.perf_counter()
    return (t1 - t0) * 1000.0


def load_json(path: Path) -> dict:
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main() -> int:
    cold_ms = measure_cli_cold_start()
    gen_ms = measure_template_generation()

    results = {"cli_cold_ms": cold_ms, "template_gen_ms": gen_ms, "ts": time.time()}
    save_json(RESULTS_PATH, results)

    baseline = load_json(BASELINE_PATH)
    if not baseline:
        # First run: create baseline
        save_json(BASELINE_PATH, results)
        print(f"[perf] baseline created: {results}")
        return 0

    def regression(curr: float, base: float) -> float:
        if base <= 0:
            return 0.0
        return ((curr - base) / base) * 100.0

    cold_reg = regression(cold_ms, baseline.get("cli_cold_ms", cold_ms))
    gen_reg = regression(gen_ms, baseline.get("template_gen_ms", gen_ms))

    print(f"[perf] cold_start: {cold_ms:.2f} ms (Δ {cold_reg:+.1f}%)")
    print(f"[perf] template_gen: {gen_ms:.2f} ms (Δ {gen_reg:+.1f}%)")

    fail = any(x > 5.0 for x in (cold_reg, gen_reg))
    if fail:
        print("[perf] regression > 5% detected", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

