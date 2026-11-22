param([string]$Symbol = "XAUUSD", [string]$Python = ".\.venv\Scripts\python.exe")
$ErrorActionPreference = "Stop"
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    & $Python -m aurum.cli run --symbol $Symbol
    if ($LASTEXITCODE -ne 0) { throw "AI runtime belum tersedia pada scaffolding. Lihat AU-020/AU-021." }
} finally { Pop-Location }
