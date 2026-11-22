param([string]$Python = "py")
$ErrorActionPreference = "Stop"
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Gagal membuat .venv. Pastikan Python 3.11+ tersedia." }
    & .\.venv\Scripts\python.exe -m pip install -e '.[dev]'
    if ($LASTEXITCODE -ne 0) { throw "Instalasi dependensi gagal." }
    & .\.venv\Scripts\python.exe -m aurum.cli doctor --offline
    if ($LASTEXITCODE -ne 0) { throw "Diagnostik offline gagal." }
} finally { Pop-Location }
