param([string]$Python = ".\.venv\Scripts\python.exe")
$ErrorActionPreference = "Stop"
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    & $Python scripts/test_offline.py
    if ($LASTEXITCODE -ne 0) { throw "Tes offline gagal." }
} finally { Pop-Location }
