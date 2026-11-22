"""Run the same offline checks locally and in GitHub Actions."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = ("python", "tests", "scripts", "dashboard")
SAFETY_MODULES = ("config", "cli", "data_quality", "mt5_client")
MIN_SAFETY_COVERAGE = 90


def run_module(*args: str) -> None:
    subprocess.run([sys.executable, "-m", *args], cwd=ROOT, check=True)


def main() -> int:
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    for name in ("pytest.xml", "coverage.xml", ".coverage"):
        (reports / name).unlink(missing_ok=True)

    try:
        run_module("ruff", "check", *SOURCE_DIRS)
        run_module("ruff", "format", "--check", *SOURCE_DIRS)
        run_module("mypy")
        run_module("aurum.cli", "doctor", "--offline")
        run_module("coverage", "run", "-m", "pytest", "-q", "--junitxml=reports/pytest.xml")
        run_module("coverage", "xml", "-o", "reports/coverage.xml")
        for module in SAFETY_MODULES:
            run_module(
                "coverage",
                "report",
                "--show-missing",
                f"--fail-under={MIN_SAFETY_COVERAGE}",
                str(Path("python", "aurum", f"{module}.py")),
            )
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
