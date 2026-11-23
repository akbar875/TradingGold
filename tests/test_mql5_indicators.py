import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_mql5_indicator_contract_with_stubbed_terminal(tmp_path):
    compiler = shutil.which("g++") or shutil.which("clang++")
    if compiler is None:
        pytest.skip("C++ compiler unavailable for the stubbed MQL5 contract test")
    executable = tmp_path / "mql5_indicators.exe"
    build = subprocess.run(
        [
            compiler,
            "-std=c++17",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(ROOT / "mt5/Include"),
            str(ROOT / "tests/fixtures/mql5_indicators.cpp"),
            "-o",
            str(executable),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert build.returncode == 0, build.stdout + build.stderr
    result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stdout + result.stderr
