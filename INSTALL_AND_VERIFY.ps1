$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Executable,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & $Executable @Arguments

    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE`: $Executable $($Arguments -join ' ')"
    }
}

Write-Host '==> Python preflight'
Invoke-Checked -Executable 'python' -Arguments @('--version')

if (-not (Test-Path '.venv')) {
    Invoke-Checked -Executable 'python' -Arguments @('-m', 'venv', '.venv')
}

$Py = Join-Path $Root '.venv\Scripts\python.exe'

Invoke-Checked -Executable $Py -Arguments @(
    '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools>=84.0.0', 'wheel'
)

Invoke-Checked -Executable $Py -Arguments @(
    '-m', 'pip', 'install', '-e', '.[dev]'
)

if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    Write-Host 'Created .env from .env.example. Replace demo secrets before exposing publicly.'
}

Write-Host '==> Tests + coverage'
Invoke-Checked -Executable $Py -Arguments @(
    '-m', 'pytest',
    '--cov=app',
    '--cov-report=term-missing',
    '--cov-fail-under=85'
)

Write-Host '==> Ruff lint'
Invoke-Checked -Executable $Py -Arguments @(
    '-m', 'ruff', 'check', '.'
)

Write-Host '==> Ruff format check'
Invoke-Checked -Executable $Py -Arguments @(
    '-m', 'ruff', 'format', '--check', '.'
)

Write-Host '==> Type checks'
Invoke-Checked -Executable $Py -Arguments @(
    '-m', 'mypy', 'app'
)

Write-Host '==> Dependency audit'
Invoke-Checked -Executable $Py -Arguments @(
    '-m', 'pip_audit'
)

Write-Host '==> Smoke test'
Invoke-Checked -Executable $Py -Arguments @(
    'scripts\smoke_test.py'
)

Write-Host ''
Write-Host 'ALL LOCAL QUALITY GATES PASSED.' -ForegroundColor Green
Write-Host 'To run the API:'
Write-Host "  & '$Py' -m uvicorn app.main:app --reload"

