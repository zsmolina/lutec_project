$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$EnvFile = Join-Path $Backend ".env"

if (-not (Test-Path $EnvFile)) {
    Write-Host "No existe backend\.env. Copie backend\.env.example y configure OPENAI_API_KEY." -ForegroundColor Yellow
    exit 1
}

$venvPython = Join-Path $Backend ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Creando entorno virtual..." -ForegroundColor Cyan
    python -m venv (Join-Path $Backend ".venv")
    & $venvPython -m pip install -r (Join-Path $Backend "requirements.txt") -q
}

Write-Host "Iniciando backend en http://127.0.0.1:8000" -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    param($dir, $py)
    Set-Location $dir
    & $py -m uvicorn app.main:app --reload --port 8000
} -ArgumentList $Backend, $venvPython

Start-Sleep -Seconds 2

Write-Host "Iniciando frontend en http://localhost:5173" -ForegroundColor Green
Set-Location $Frontend
npm run dev

Stop-Job $backendJob -ErrorAction SilentlyContinue
Remove-Job $backendJob -ErrorAction SilentlyContinue
