"""Exercise the real PowerShell runner with isolated compiler/process fixtures."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PWSH = shutil.which("pwsh")
pytestmark = pytest.mark.skipif(
    sys.platform != "win32" or PWSH is None, reason="Windows PowerShell runner contract"
)

WRAPPER = r"""
param([string]$Case)
$ErrorActionPreference = 'Stop'
$global:Case = $Case
function global:Start-Process {
    param($FilePath, $WindowStyle, [switch]$PassThru, $ArgumentList)
    if ($WindowStyle -ne 'Hidden' -or !$PassThru) { throw 'Invalid launch options' }
    if ($global:Case -eq 'launch-failure') { throw 'SIMULATED_LAUNCH_FAILURE' }
    $source = ($ArgumentList[0] -replace '^/compile:"','').TrimEnd('"')
    $include = ($ArgumentList[1] -replace '^/include:"','').TrimEnd('"')
    if ($ArgumentList[2] -ne '/log' -or
        !(Test-Path -LiteralPath "$include/Include/Aurum/Status.mqh")) {
        throw 'Invalid CLI or include staging'
    }
    $log = [IO.Path]::ChangeExtension($source, '.log')
    $binary = [IO.Path]::ChangeExtension($source, '.ex5')
    $summary = switch ($global:Case) {
        'ten-errors' { 'Result: 10 errors, 0 warnings' }
        'warnings' { 'Result: 0 errors, 1 warnings' }
        'embedded-text' { 'source text: 0 errors, 0 warnings' }
        'duplicate-summary' { "Result: 1 errors, 0 warnings`nResult: 0 errors, 0 warnings" }
        'error-diagnostic' { "file.mq5 : error 100: failure`nResult: 0 errors, 0 warnings" }
        'bare-summary' { '0 errors, 0 warnings, 100 msec elapsed' }
        default { "file.mq5 : information: compiling`n" +
            'Result: 0 errors, 0 warnings, 100 msec elapsed' }
    }
    if ($global:Case -ne 'no-log') {
        Set-Content -LiteralPath $log -Value $summary -Encoding Unicode
    }
    if ($global:Case -ne 'no-binary') {
        [IO.File]::WriteAllBytes($binary, [byte[]]@(1,2,3))
        if ($global:Case -eq 'empty-binary') { [IO.File]::WriteAllBytes($binary, [byte[]]@()) }
        if ($global:Case -eq 'stale-binary') {
            (Get-Item -LiteralPath $binary).LastWriteTimeUtc = [DateTime]::UtcNow.AddHours(-1)
        }
    }
    if ($global:Case -eq 'timeout') {
        # Use a real process so the timeout assertion verifies actual termination.
        $shellPath = (Get-Process -Id $PID).Path
        $child = Microsoft.PowerShell.Management\Start-Process -FilePath $shellPath `
            -WindowStyle Hidden -PassThru -ArgumentList @('-NoProfile','-Command','Start-Sleep 60')
        $child.Id | Set-Content -LiteralPath "$PSScriptRoot/child.pid"
        return $child
    }
    if ($global:Case -eq 'success') {
        # Validate WaitForExit/Refresh/ExitCode on an actual native process too.
        return Microsoft.PowerShell.Management\Start-Process `
            -FilePath (Get-Process -Id $PID).Path -WindowStyle Hidden -PassThru `
            -ArgumentList @('-NoProfile','-Command','exit 0')
    }
    $result = [pscustomobject]@{ ExitCode = $(if ($global:Case -eq 'nonzero') { 7 } else { 0 }) }
    $result | Add-Member ScriptMethod WaitForExit { param($ms) return $true }
    $result | Add-Member ScriptMethod Refresh {}
    return $result
}
$compiler = Join-Path $PSScriptRoot 'compiler.exe'
if ($Case -eq 'unavailable') { $compiler = Join-Path $PSScriptRoot 'missing.exe' }
$timeout = if ($Case -eq 'invalid-timeout') { 0 } elseif ($Case -eq 'timeout') { 1 } else { 120 }
& "$PSScriptRoot/scripts/compile_mql5.ps1" -MetaEditor $compiler -TimeoutSeconds $timeout
exit $LASTEXITCODE
"""


@pytest.mark.parametrize(
    ("case", "exit_code", "reason"),
    [
        ("success", 0, "COMPILE_VERIFIED"),
        ("bare-summary", 0, "COMPILE_VERIFIED"),
        ("unavailable", 2, "COMPILER_UNAVAILABLE"),
        ("invalid-timeout", 1, "INVALID_TIMEOUT"),
        ("missing-source", 1, "SOURCE_UNAVAILABLE"),
        ("missing-include", 1, "SOURCE_UNAVAILABLE"),
        ("launch-failure", 1, "COMPILER_LAUNCH_FAILED"),
        ("timeout", 1, "COMPILER_TIMEOUT"),
        ("nonzero", 1, "COMPILER_EXIT_NONZERO"),
        ("ten-errors", 1, "LOG_INVALID"),
        ("warnings", 1, "LOG_INVALID"),
        ("embedded-text", 1, "LOG_INVALID"),
        ("duplicate-summary", 1, "LOG_INVALID"),
        ("error-diagnostic", 1, "LOG_INVALID"),
        ("no-log", 1, "LOG_INVALID"),
        ("no-binary", 1, "ARTIFACT_INVALID"),
        ("empty-binary", 1, "ARTIFACT_INVALID"),
        ("stale-binary", 1, "ARTIFACT_INVALID"),
    ],
)
def test_compile_contract(tmp_path, case, exit_code, reason):
    root = tmp_path / "repo with spaces"
    (root / "scripts").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts/compile_mql5.ps1", root / "scripts")
    shutil.copytree(ROOT / "mt5", root / "mt5")
    if case == "missing-source":
        (root / "mt5/Experts/Aurum_Expert_AI_XAUUSD.mq5").unlink()
    if case == "missing-include":
        (root / "mt5/Include/Aurum/Status.mqh").unlink()
    # Seed old evidence; even absent new output must never reuse it.
    (root / "reports").mkdir()
    status_path = root / "reports/mql5-status.txt"
    status_path.write_text("PASS: PREVIOUS RUN", encoding="utf-8")
    old_binary = root / "mt5/Experts/Aurum_Expert_AI_XAUUSD.ex5"
    old_binary.write_bytes(b"OLD ARTIFACT")
    (root / "compiler.exe").write_bytes(b"MOCK - never executed")
    wrapper = root / "wrapper.ps1"
    wrapper.write_text(WRAPPER, encoding="utf-8")
    result = subprocess.run(
        [PWSH, "-NoProfile", "-File", str(wrapper), "-Case", case],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == exit_code, result.stdout + result.stderr
    status = status_path.read_text(encoding="utf-8-sig")
    assert reason in status
    assert "PREVIOUS RUN" not in status
    assert status.startswith({0: "PASS", 1: "FAIL", 2: "NOT RUN"}[exit_code])
    assert old_binary.read_bytes() == b"OLD ARTIFACT"
    if case == "timeout":
        child_pid = (root / "child.pid").read_text().strip()
        probe = subprocess.run(
            [PWSH, "-NoProfile", "-Command", f"Get-Process -Id {int(child_pid)} -ErrorAction Stop"],
            capture_output=True,
            timeout=10,
            check=False,
        )
        assert probe.returncode != 0, "Compiler process survived timeout"
    if exit_code == 0:
        artifacts = list((root / "reports/mql5").rglob("*.ex5"))
        assert len(artifacts) == 1
        assert str(artifacts[0]) in status
    assert os.fspath(root) in status or case in {
        "unavailable",
        "invalid-timeout",
        "missing-source",
        "missing-include",
    }
