param([string]$MetaEditor = $env:METAEDITOR_PATH)
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path $PSScriptRoot -Parent
$reportDir = Join-Path $repoRoot "reports"
New-Item -ItemType Directory -Force $reportDir | Out-Null
$statusPath = Join-Path $reportDir "mql5-status.txt"
if (!$MetaEditor -or !(Test-Path -LiteralPath $MetaEditor -PathType Leaf)) {
    "NOT RUN (environment unavailable): tentukan -MetaEditor atau METAEDITOR_PATH." |
        Set-Content -LiteralPath $statusPath
    Get-Content -LiteralPath $statusPath
    exit 2
}
$source = Join-Path $repoRoot "mt5\Experts\Aurum_Expert_AI_XAUUSD.mq5"
$include = Join-Path $repoRoot "mt5"
$log = Join-Path $reportDir ("compile-" + [guid]::NewGuid().ToString("N") + ".log")
$binary = [IO.Path]::ChangeExtension($source, ".ex5")
$started = [DateTime]::UtcNow
$proc = Start-Process -FilePath $MetaEditor -WindowStyle Hidden -PassThru -Wait -ArgumentList @(
    "/compile:`"$source`"", "/inc:`"$include`"", "/log:`"$log`""
)
$logText = if (Test-Path -LiteralPath $log) { Get-Content -LiteralPath $log -Raw } else { "" }
$freshBinary = (Test-Path -LiteralPath $binary) -and
    ((Get-Item -LiteralPath $binary).LastWriteTimeUtc -ge $started)
if ($proc.ExitCode -eq 0 -and $freshBinary -and $logText -match '0 errors, 0 warnings') {
    "PASS: MetaEditor exit=$($proc.ExitCode); log=$log" | Set-Content -LiteralPath $statusPath
    Get-Content -LiteralPath $statusPath
} else {
    "FAIL: compile tidak terverifikasi; exit=$($proc.ExitCode); log=$log" |
        Set-Content -LiteralPath $statusPath
    Get-Content -LiteralPath $statusPath
    exit 1
}
