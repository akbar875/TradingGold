param([string]$Python = ".\.venv\Scripts\python.exe")
$ErrorActionPreference = "Stop"
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    & $Python -m ruff check python tests scripts dashboard
    if ($LASTEXITCODE -ne 0) { throw "Lint gagal." }
    & $Python -m ruff format --check python tests scripts dashboard
    if ($LASTEXITCODE -ne 0) { throw "Format gagal." }
    & $Python -m mypy
    if ($LASTEXITCODE -ne 0) { throw "Type check gagal." }
    New-Item -ItemType Directory -Force reports | Out-Null
    & $Python -m pytest -q --junitxml=reports/pytest.xml
    if ($LASTEXITCODE -ne 0) { throw "Tes offline gagal." }
} finally { Pop-Location }
