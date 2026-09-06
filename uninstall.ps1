# Bailanysta — Uninstall (safe by default, preserves data)
param(
    [switch]$RemoveVolumes,
    [switch]$NonInteractive
)
$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot) { $ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }
Set-Location -LiteralPath $ProjectRoot

function Write-Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Ok($m){ Write-Host "[OK] $m" -ForegroundColor Green }
function Write-Warn($m){ Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err($m){ Write-Host "[ERR] $m" -ForegroundColor Red }

Write-Host "========================================" -ForegroundColor White
Write-Host " Bailanysta — Uninstall" -ForegroundColor White
Write-Host "========================================" -ForegroundColor White
Write-Host ""
Write-Warn "Контейнеры будут остановлены, но данные PostgreSQL и uploads СОХРАНЯТСЯ."
Write-Host " Volumes: postgres_data, uploads_data — остаются." -ForegroundColor Gray
Write-Host ""

if ($RemoveVolumes) {
    Write-Err "ВНИМАНИЕ: --RemoveVolumes удалит ВСЕ данные БД и uploads безвозвратно!"
    if (-not $NonInteractive) {
        $ans = Read-Host "Точно удалить volumes? Введи YES для подтверждения"
        if ($ans -ne "YES") { Write-Warn "Отменено."; exit 0 }
    }
    Write-Info "Остановка с удалением volumes..."
    docker compose -f docker-compose.prod.yml down -v
    Write-Warn "Volumes удалены. Данные потеряны."
    exit 0
}

Write-Info "Остановка контейнеров (down без -v)..."
docker compose -f docker-compose.prod.yml down
if ($LASTEXITCODE -ne 0) { Write-Err "down failed"; exit 1 }
Write-Ok "Контейнеры остановлены. Данные сохранены в volumes."
Write-Host ""
Write-Host "Чтобы полностью удалить данные, запусти:" -ForegroundColor Gray
Write-Host "  .\uninstall.ps1 -RemoveVolumes" -ForegroundColor White
Write-Host "  или" -ForegroundColor Gray
Write-Host "  docker compose -f docker-compose.prod.yml down -v" -ForegroundColor White
Write-Host ""
Write-Host "Чтобы удалить только images:" -ForegroundColor Gray
Write-Host "  docker images | findstr bailanysta" -ForegroundColor White
