$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host '==> Python preflight'
python --version

if (-not (Test-Path '.venv')) {
    python -m venv .venv
}

$Py = Join-Path $Root '.venv\Scripts\python.exe'
& $Py -m pip install --upgrade pip
& $Py -m pip install -e '.[dev]'

if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    Write-Host 'Created .env from .env.example. Replace demo secrets before exposing publicly.'
}

Write-Host '==> Tests + coverage'
& $Py -m pytest --cov=app --cov-report=term-missing --cov-fail-under=85

Write-Host '==> Lint + type checks'
& $Py -m ruff check .
& $Py -m ruff format --check .
& $Py -m mypy app

Write-Host '==> Smoke test'
& $Py scripts\smoke_test.py

Write-Host ''
Write-Host 'PASS. To run the API:'
Write-Host "  & '$Py' -m uvicorn app.main:app --reload"
