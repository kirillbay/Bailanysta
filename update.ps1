# Bailanysta — Update (safe, preserves .env and volumes)
param([switch]$NonInteractive)
$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot) { $ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }
Set-Location -LiteralPath $ProjectRoot

function Write-Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Ok($m){ Write-Host "[OK] $m" -ForegroundColor Green }
function Write-Warn($m){ Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err($m){ Write-Host "[ERR] $m" -ForegroundColor Red }

Write-Host "========================================" -ForegroundColor White
Write-Host " Bailanysta — Update" -ForegroundColor White
Write-Host "========================================" -ForegroundColor White

if (-not (Test-Path -LiteralPath ".env")) { Write-Warn ".env не найден — будет создан из .env.example при необходимости" }
else { Write-Ok ".env сохранён — не трогаю (безопасность)" }

Write-Info "Проверка git (если репозиторий)..."
if (Test-Path -LiteralPath ".git") {
    try {
        git status --porcelain
        Write-Info "Если есть локальные изменения — сохрани их перед pull"
        if (-not $NonInteractive) {
            $ans = Read-Host "Выполнить git pull? (y/N)"
            if ($ans -eq "y" -or $ans -eq "Y") {
                git pull
            } else { Write-Warn "git pull пропущен" }
        }
    } catch { Write-Warn "git pull не выполнен: $_" }
} else {
    Write-Warn "Не git репозиторий — пропускаю git pull (скопируй новые файлы вручную)"
}

Write-Info "Валидация compose..."
docker compose -f docker-compose.prod.yml config 1>$null
if ($LASTEXITCODE -ne 0) { Write-Err "config failed"; exit 1 }
Write-Ok "config OK"

Write-Info "Сборка (build)..."
docker compose -f docker-compose.prod.yml build
if ($LASTEXITCODE -ne 0) { Write-Err "build failed"; exit 1 }

Write-Info "Перезапуск (up -d) — миграции выполнятся автоматически..."
docker compose -f docker-compose.prod.yml up -d
if ($LASTEXITCODE -ne 0) { Write-Err "up failed"; exit 1 }

Write-Info "Ожидание healthchecks 20с..."
Start-Sleep -Seconds 20
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=100

Write-Ok "Update завершён. .env и volumes сохранены."
Write-Host " Health: http://localhost:8000/health" -ForegroundColor White
Write-Host " Frontend: http://localhost" -ForegroundColor White
