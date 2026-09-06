# Bailanysta — Production Installer (PowerShell)
# MVP: No new features, no secrets in Git, safe for existing data
# Requires: Windows 10/11, Docker Desktop + WSL2, Git (optional)
# Location: C:\Users\lueex\Desktop\Bailanysta\install.ps1

param(
    [switch]$NonInteractive
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot -or $ProjectRoot -eq "") { $ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }
Set-Location -LiteralPath $ProjectRoot

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[ERR] $msg" -ForegroundColor Red }

function Test-Command($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

Write-Host "========================================" -ForegroundColor White
Write-Host " Bailanysta — Production Installer" -ForegroundColor White
Write-Host " Project: $ProjectRoot" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor White
Write-Host ""

# 1. Windows check
Write-Info "1/13 Проверка Windows..."
if ($env:OS -notlike "*Windows*") {
    Write-Err "Этот установщик предназначен для Windows. Обнаружено: $env:OS"
    exit 1
}
Write-Ok "Windows: $env:OS (Build $([Environment]::OSVersion.Version))"

# 2. Docker Desktop check
Write-Info "2/13 Проверка Docker Desktop..."
if (-not (Test-Command "docker")) {
    Write-Warn "Docker не найден в PATH."
    Write-Host ""
    Write-Host "Официальная установка:" -ForegroundColor White
    Write-Host "  1) Скачай Docker Desktop с официального сайта:" -ForegroundColor Gray
    Write-Host "     https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
    Write-Host "     Документация: https://docs.docker.com/desktop/setup/install/windows-install/" -ForegroundColor Cyan
    Write-Host "  2) Требования: Windows 10/11 64-bit, WSL2, виртуализация включена в BIOS" -ForegroundColor Gray
    Write-Host "  3) Альтернативно через winget (требует подтверждения):" -ForegroundColor Gray
    Write-Host "     winget install -e --id Docker.DockerDesktop" -ForegroundColor White
    Write-Host ""
    Write-Host "  WSL2 (если нужен): https://learn.microsoft.com/en-us/windows/wsl/install" -ForegroundColor Cyan
    Write-Host "     wsl --install  (требует перезагрузку)" -ForegroundColor White
    Write-Host ""
    Write-Warn "После установки Docker Desktop перезапусти PowerShell и запусти install.bat снова."
    Write-Warn "Установка остановлена — Docker обязателен для Bailanysta production."
    exit 1
}
try { $dockerVer = docker --version 2>&1 } catch { $dockerVer = "unknown" }
Write-Ok "Docker: $dockerVer"

# 3. Docker Compose check
Write-Info "3/13 Проверка Docker Compose..."
$composeOk = $false
try {
    $c1 = docker compose version 2>&1
    if ($LASTEXITCODE -eq 0) { $composeOk = $true; Write-Ok "Docker Compose: $c1" }
} catch {}
if (-not $composeOk) {
    try {
        $c2 = docker-compose --version 2>&1
        if ($LASTEXITCODE -eq 0) { $composeOk = $true; Write-Ok "Docker Compose (standalone): $c2" }
    } catch {}
}
if (-not $composeOk) {
    Write-Err "Docker Compose не найден. Установи Docker Desktop (включает Compose v2)."
    exit 1
}

# 4. Docker daemon
Write-Info "4/13 Проверка Docker daemon..."
try {
    docker info 1>$null 2>&1
    if ($LASTEXITCODE -ne 0) { throw "daemon not running" }
    Write-Ok "Docker daemon запущен"
} catch {
    Write-Err "Docker daemon не запущен. Открой Docker Desktop и дождись статуса Running."
    Write-Host "  Подсказка: запусти Docker Desktop из меню Пуск, дождись 30-60 сек." -ForegroundColor Gray
    exit 1
}

# 5. WSL2 info (не критично, но полезно)
Write-Info "5/13 Проверка WSL2..."
try {
    $wslOut = wsl --status 2>&1 | Out-String
    Write-Host $wslOut -ForegroundColor Gray
} catch {
    Write-Warn "WSL статус не удалось получить (не критично, но Docker Desktop требует WSL2). См. https://learn.microsoft.com/en-us/windows/wsl/install"
}

# 6. Структура Bailanysta
Write-Info "6/13 Проверка структуры Bailanysta..."
$required = @("docker-compose.prod.yml", "backend", "frontend")
foreach ($p in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot $p))) {
        Write-Err "Не найден обязательный путь: $p (ожидается в $ProjectRoot)"
        exit 1
    }
}
Write-Ok "Структура: docker-compose.prod.yml, backend/, frontend/ — найдены"

# 7. docker-compose.prod.yml exists already checked, validate config
Write-Info "7/13 Проверка docker-compose.prod.yml..."
if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot "docker-compose.prod.yml"))) {
    Write-Err "docker-compose.prod.yml не найден"
    exit 1
}
Write-Ok "docker-compose.prod.yml найден"

# 8. .env handling — не перезаписывать без подтверждения
Write-Info "8/13 Проверка .env..."
$envPath = Join-Path $ProjectRoot ".env"
$envExample = Join-Path $ProjectRoot ".env.example"
if (-not (Test-Path -LiteralPath $envPath)) {
    if (Test-Path -LiteralPath $envExample) {
        Copy-Item -LiteralPath $envExample -Destination $envPath
        Write-Ok ".env создан из .env.example — заполни значения"
    } else {
        New-Item -ItemType File -Path $envPath -Force | Out-Null
        Write-Warn ".env.example не найден, создан пустой .env"
    }
} else {
    Write-Ok ".env уже существует — не перезаписывается (безопасность)"
    Write-Host "  Проверь вручную: $envPath" -ForegroundColor Gray
}

# 9. SECRET_KEY generation (криптографически безопасно)
Write-Info "9/13 Проверка SECRET_KEY..."
$needSecret = $false
if (Test-Path -LiteralPath $envPath) {
    $envContent = Get-Content -LiteralPath $envPath -Raw -ErrorAction SilentlyContinue
    if (-not $envContent) { $envContent = "" }
    if ($envContent -match "SECRET_KEY=change-me" -or $envContent -match "SECRET_KEY=\s*$" -or $envContent -notmatch "SECRET_KEY=") {
        $needSecret = $true
    }
}
if ($needSecret) {
    Write-Warn "SECRET_KEY не задан или placeholder — генерирую..."
    $newSecret = $null
    # Try Python secrets
    if (Test-Command "python") {
        try { $newSecret = python -c "import secrets; print(secrets.token_hex(32))" 2>$null } catch {}
    }
    if (-not $newSecret -and (Test-Command "python3")) {
        try { $newSecret = python3 -c "import secrets; print(secrets.token_hex(32))" 2>$null } catch {}
    }
    if (-not $newSecret) {
        # PowerShell fallback: 32 bytes hex
        $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        $bytes = New-Object byte[] 32
        $rng.GetBytes($bytes)
        $newSecret = -join ($bytes | ForEach-Object { $_.ToString("x2") })
    }
    $newSecret = $newSecret.Trim()
    if ($newSecret.Length -lt 32) { Write-Err "Не удалось сгенерировать SECRET_KEY"; exit 1 }

    # Update .env safely — replace line
    $lines = @()
    $found = $false
    if (Test-Path -LiteralPath $envPath) {
        $lines = Get-Content -LiteralPath $envPath
    }
    $out = @()
    foreach ($line in $lines) {
        if ($line -match "^SECRET_KEY=") {
            $out += "SECRET_KEY=$newSecret"
            $found = $true
        } else {
            $out += $line
        }
    }
    if (-not $found) { $out += "SECRET_KEY=$newSecret" }
    # Ensure APP_ENV=production for prod
    $hasAppEnv = $false
    for ($i=0; $i -lt $out.Count; $i++) {
        if ($out[$i] -match "^APP_ENV=") { $out[$i] = "APP_ENV=production"; $hasAppEnv = $true }
        if ($out[$i] -match "^DEBUG=") { $out[$i] = "DEBUG=false" }
    }
    if (-not $hasAppEnv) { $out += "APP_ENV=production"; $out += "DEBUG=false" }
    Set-Content -LiteralPath $envPath -Value ($out -join "`n") -Encoding UTF8
    Write-Ok "SECRET_KEY сгенерирован и записан в .env (production, `>=32` hex)"
} else {
    Write-Ok "SECRET_KEY уже задан — не трогаю"
}

# Validate required env vars for production
Write-Info "Проверка обязательных переменных..."
$envMap = @{}
if (Test-Path -LiteralPath $envPath) {
    Get-Content -LiteralPath $envPath | ForEach-Object {
        if ($_ -match "^\s*#" -or $_ -notmatch "=") { return }
        $kv = $_ -split "=",2
        if ($kv.Count -eq 2) { $envMap[$kv[0].Trim()] = $kv[1].Trim() }
    }
}
$requiredVars = @("DATABASE_URL", "SECRET_KEY", "CORS_ORIGINS", "VITE_API_URL")
$missing = @()
foreach ($k in $requiredVars) {
    $v = $envMap[$k]
    if (-not $v -or $v -eq "" -or $v -like "*change-me*") {
        # Also check OS env
        $osVal = [Environment]::GetEnvironmentVariable($k)
        if (-not $osVal) { $missing += $k }
    }
}
if ($missing.Count -gt 0) {
    Write-Warn ("Не заданы обязательные переменные: " + ($missing -join ", "))
    Write-Host "  Заполни .env вручную. Пример:" -ForegroundColor Gray
    Write-Host "    DATABASE_URL=postgresql+psycopg://bailanysta:STRONGPASS@postgres:5432/bailanysta" -ForegroundColor White
    Write-Host "    CORS_ORIGINS=https://bailanysta.example.com" -ForegroundColor White
    Write-Host "    VITE_API_URL=https://api.bailanysta.example.com" -ForegroundColor White
    if (-not $NonInteractive) {
        $ans = Read-Host "Продолжить без этих переменных? (y/N)"
        if ($ans -ne "y" -and $ans -ne "Y") { Write-Err "Установка прервана — заполни .env и запусти снова."; exit 1 }
    }
} else {
    Write-Ok "Обязательные переменные присутствуют"
}

# 10. Validate compose config
Write-Info "10/13 Валидация docker-compose.prod.yml..."
try {
    docker compose -f docker-compose.prod.yml config 1>$null
    if ($LASTEXITCODE -ne 0) { throw "config failed" }
    Write-Ok "docker compose config — OK"
} catch {
    Write-Err "docker compose config — FAILED. Проверь docker-compose.prod.yml и .env"
    docker compose -f docker-compose.prod.yml config
    exit 1
}

# 11. Build
Write-Info "11/13 Сборка images (может занять 2-5 мин)..."
try {
    docker compose -f docker-compose.prod.yml build
    if ($LASTEXITCODE -ne 0) { throw "build failed" }
    Write-Ok "Build — OK"
} catch {
    Write-Err "Build FAILED — см. лог выше"
    exit 1
}

# 12. Up
Write-Info "12/13 Запуск stack (up -d)..."
try {
    docker compose -f docker-compose.prod.yml up -d
    if ($LASTEXITCODE -ne 0) { throw "up failed" }
    Write-Ok "Containers started"
} catch {
    Write-Err "up -d FAILED"
    docker compose -f docker-compose.prod.yml logs --tail=100
    exit 1
}

# 13. Healthchecks
Write-Info "13/13 Проверка healthchecks (ожидание 30с)..."
Start-Sleep -Seconds 15
# Retry loop 30s
$max = 6
$ok = $false
for ($i=1; $i -le $max; $i++) {
    try {
        $ps = docker compose -f docker-compose.prod.yml ps --format json 2>&1
        Write-Host $ps -ForegroundColor Gray
    } catch {}
    # Check health via logs
    try {
        $health = docker inspect --format="{{if .State.Health}}{{json .State.Health.Status}}{{end}}" bailanysta-backend 2>&1
        if ($health -match "healthy") { $ok = $true; break }
    } catch {}
    Start-Sleep -Seconds 5
}
docker compose -f docker-compose.prod.yml ps
Write-Host ""
docker compose -f docker-compose.prod.yml logs --tail=100

# Try backend health endpoints
Write-Info "Проверка backend health endpoints..."
$apiUrl = $envMap["VITE_API_URL"]
if (-not $apiUrl) { $apiUrl = "http://localhost:8000" }
# Try localhost:8000 directly (backend port)
$healthUrls = @("http://localhost:8000/health", "http://localhost:8000/api/v1/health", "http://localhost:8000/api/v1/health/db")
foreach ($u in $healthUrls) {
    try {
        $r = Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($r.StatusCode -eq 200) { Write-Ok "Health $u — 200" } else { Write-Warn "Health $u — $($r.StatusCode)" }
    } catch {
        Write-Warn "Health $u — not reachable (maybe behind proxy, check docker logs)"
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Bailanysta — Установка завершена!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host " Frontend: http://localhost (nginx)" -ForegroundColor White
if ($apiUrl) { Write-Host " Backend:  $apiUrl" -ForegroundColor White }
Write-Host " Health:   http://localhost:8000/health" -ForegroundColor White
Write-Host " Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Команды:" -ForegroundColor Gray
Write-Host "  Логи:      docker compose -f docker-compose.prod.yml logs -f" -ForegroundColor White
Write-Host "  Остановить: docker compose -f docker-compose.prod.yml down    (данные сохранятся)" -ForegroundColor White
Write-Host "  Обновить:   .\update.bat  (или .\update.ps1)" -ForegroundColor White
Write-Host "  Удалить:    .\uninstall.bat" -ForegroundColor White
Write-Host ""

# Try open browser
try {
    $frontendUrl = "http://localhost"
    Write-Info "Попытка открыть $frontendUrl в браузере..."
    Start-Process $frontendUrl -ErrorAction SilentlyContinue
} catch {}

Write-Ok "Готово. Если видишь контейнеры healthy — Bailanysta работает."
