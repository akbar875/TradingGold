param(
    [string]$MetaEditor = $env:METAEDITOR_PATH,
    [int]$TimeoutSeconds = 120
)
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path $PSScriptRoot -Parent
$reportDir = Join-Path $repoRoot "reports"
New-Item -ItemType Directory -Force $reportDir | Out-Null
$statusPath = Join-Path $reportDir "mql5-status.txt"
$runId = [guid]::NewGuid().ToString("N")
$runDir = Join-Path $reportDir "mql5/$runId"
$reason = "BUILD_SETUP_FAILED"
$proc = $null
$exitCode = $null
$log = $null
$binary = $null
# Invalidate previous evidence before checking inputs or launching the compiler.
"NOT RUN | BUILD_STARTED | run=$runId" | Set-Content -LiteralPath $statusPath
try {
    if (!$MetaEditor -or !(Test-Path -LiteralPath $MetaEditor -PathType Leaf)) {
        "NOT RUN | COMPILER_UNAVAILABLE | tentukan -MetaEditor atau METAEDITOR_PATH; run=$runId" |
            Set-Content -LiteralPath $statusPath
        Get-Content -LiteralPath $statusPath
        exit 2
    }
    if ($TimeoutSeconds -lt 1 -or $TimeoutSeconds -gt 600) {
        $reason = "INVALID_TIMEOUT"
        throw "TimeoutSeconds harus 1..600."
    }
    $MetaEditor = (Resolve-Path -LiteralPath $MetaEditor).Path
    $sourceName = "Aurum_Expert_AI_XAUUSD.mq5"
    $originalSource = Join-Path $repoRoot "mt5/Experts/$sourceName"
    $originalInclude = Join-Path $repoRoot "mt5/Include"
    if (!(Test-Path -LiteralPath $originalSource -PathType Leaf) -or
        !(Test-Path -LiteralPath (Join-Path $originalInclude "Aurum/Status.mqh") -PathType Leaf)) {
        $reason = "SOURCE_UNAVAILABLE"
        throw "Source EA atau include wajib tidak ditemukan."
    }
    # A unique workspace prevents an old EX5 or log from satisfying a new build.
    $buildRoot = Join-Path $runDir "MQL5"
    New-Item -ItemType Directory -Force (Join-Path $buildRoot "Experts") | Out-Null
    Copy-Item -LiteralPath $originalSource -Destination (Join-Path $buildRoot "Experts")
    Copy-Item -LiteralPath $originalInclude -Destination $buildRoot -Recurse
    $source = Join-Path $buildRoot "Experts/$sourceName"
    $log = [IO.Path]::ChangeExtension($source, ".log")
    $binary = [IO.Path]::ChangeExtension($source, ".ex5")
    $started = [DateTime]::UtcNow
    $reason = "COMPILER_LAUNCH_FAILED"
    # /include and /log follow the documented MetaEditor CLI contract.
    $proc = Start-Process -FilePath $MetaEditor -WindowStyle Hidden -PassThru -ArgumentList @(
        "/compile:`"$source`"", "/include:`"$buildRoot`"", "/log"
    )
    $reason = "COMPILER_WAIT_FAILED"
    if (!$proc.WaitForExit($TimeoutSeconds * 1000)) {
        $reason = "COMPILER_TIMEOUT"
        Stop-Process -Id $proc.Id -Force -ErrorAction Stop
        throw "Compiler melewati batas waktu $TimeoutSeconds detik."
    }
    $proc.Refresh()
    $exitCode = $proc.ExitCode
    $reason = "COMPILER_EXIT_NONZERO"
    if ($exitCode -ne 0) { throw "Compiler exit nonzero." }
    $reason = "LOG_INVALID"
    if (!(Test-Path -LiteralPath $log -PathType Leaf)) { throw "Log compiler tidak tersedia." }
    $logText = Get-Content -LiteralPath $log -Raw
    $summary = [regex]::Matches($logText,
        '(?m)^\s*(?:Result:\s*)?(\d+) errors?, (\d+) warnings?(?:,[^\r\n]*)?\s*$')
    if ($summary.Count -ne 1 -or $summary[0].Groups[1].Value -ne "0" -or
        $summary[0].Groups[2].Value -ne "0" -or
        $logText -match '(?im)^.*\berror\s+(?:\d+|:)') {
        throw "Ringkasan compiler harus tunggal, 0 errors dan 0 warnings."
    }
    $reason = "ARTIFACT_INVALID"
    if (!(Test-Path -LiteralPath $binary -PathType Leaf)) { throw "EX5 tidak tersedia." }
    $artifact = Get-Item -LiteralPath $binary
    if ($artifact.Length -eq 0 -or $artifact.LastWriteTimeUtc -lt $started) {
        throw "EX5 kosong atau bukan artifact baru."
    }
    "PASS | COMPILE_VERIFIED | exit=$exitCode; run=$runId; log=$log; artifact=$binary" |
        Set-Content -LiteralPath $statusPath
    Get-Content -LiteralPath $statusPath
    exit 0
} catch {
    "FAIL | $reason | exit=$exitCode; run=$runId; log=$log; artifact=$binary; detail=$($_.Exception.Message)" |
        Set-Content -LiteralPath $statusPath
    Get-Content -LiteralPath $statusPath
    exit 1
} finally {
    if ($null -ne $proc -and $proc -is [System.IDisposable]) { $proc.Dispose() }
}
