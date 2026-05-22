# Arranca backend + frontend. Delega al script de la raíz del monorepo.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$DevScript = Join-Path $Root "scripts\dev.ps1"

if (-not (Test-Path $DevScript)) {
    Write-Host "No se encontró $DevScript" -ForegroundColor Red
    exit 1
}

& $DevScript
