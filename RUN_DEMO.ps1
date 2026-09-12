$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
$Py = Join-Path $Root '.venv\Scripts\python.exe'
if (-not (Test-Path $Py)) {
    throw 'Run .\INSTALL_AND_VERIFY.ps1 first.'
}
& $Py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
