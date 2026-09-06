# Bailanysta - One-Click Installer (Windows)
# Supports: Quick Start (SQLite, no Docker) for reviewers + Production (Docker) for advanced
# Location: C:\Users\lueex\Desktop\Bailanysta\install.ps1

param([switch]$NonInteractive, [switch]$Production)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot) { $ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }
Set-Location -LiteralPath $ProjectRoot

function Write-Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Ok($m){ Write-Host "[OK] $m" -ForegroundColor Green }
function Write-Warn($m){ Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err($m){ Write-Host "[ERR] $m" -ForegroundColor Red }
function Test-Cmd($n){ return [bool](Get-Command $n -ErrorAction SilentlyContinue) }

Write-Host "========================================" -ForegroundColor White
Write-Host " Bailanysta - One-Click Installer" -ForegroundColor White
Write-Host " Project: $ProjectRoot" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor White
Write-Host ""

# Detect mode
$hasNode = Test-Cmd "node"
$hasPython = (Test-Cmd "python") -or (Test-Cmd "python3")
$hasDocker = Test-Cmd "docker"
$hasCompose = $false
if ($hasDocker) {
    try { docker compose version 1>$null 2>&1; if ($LASTEXITCODE -eq 0) { $hasCompose = $true } } catch {}
}

Write-Info "Environment:"
Write-Host "  Node:    $(if ($hasNode) { (node --version 2>&1) } else { 'NOT FOUND' })" -ForegroundColor Gray
Write-Host "  Python:  $(if ($hasPython) { try { (python --version 2>&1) } catch { (python3 --version 2>&1) } } else { 'NOT FOUND' })" -ForegroundColor Gray
Write-Host "  Docker:  $(if ($hasDocker) { try { (docker --version 2>&1) } catch { 'unknown' } } else { 'NOT FOUND' })" -ForegroundColor Gray
Write-Host "  Compose: $(if ($hasCompose) { 'YES' } else { 'NO' })" -ForegroundColor Gray
Write-Host ""

# Choose mode
$mode = "quick"
if ($Production -and $hasDocker -and $hasCompose) {
    $mode = "production"
} elseif (-not $hasNode -or -not $hasPython) {
    if ($hasDocker -and $hasCompose) {
        $mode = "production"
        Write-Warn "Node/Python not found, but Docker exists - switching to Production."
    } else {
        Write-Err "Node.js and Python not found, and no Docker."
        Write-Host "For Quick Start install:" -ForegroundColor White
        Write-Host "  Node.js 20+ : https://nodejs.org/" -ForegroundColor Cyan
        Write-Host "  Python 3.12+: https://www.python.org/downloads/" -ForegroundColor Cyan
        Write-Host "Or Docker Desktop: https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
        exit 1
    }
} else {
    if ($hasDocker -and $hasCompose -and -not $NonInteractive) {
        Write-Host "Found Node, Python and Docker. Choose mode:" -ForegroundColor White
        Write-Host "  [1] Quick Start (SQLite, no Docker) - for reviewer, 1 click" -ForegroundColor Green
        Write-Host "  [2] Production (Docker: postgres+backend+frontend)" -ForegroundColor Gray
        $choice = Read-Host "Enter 1 or 2 (default 1)"
        if ($choice -eq "2") { $mode = "production" } else { $mode = "quick" }
    } elseif ($hasDocker -and $hasCompose) {
        $mode = "quick"
    }
}

Write-Host ""
Write-Info "Selected mode: $mode"
Write-Host ""

if ($mode -eq "production") {
    Write-Host "=== Production (Docker) ===" -ForegroundColor White
    if (-not $hasDocker) { Write-Err "Docker not found"; exit 1 }
    try { docker info 1>$null 2>&1; if ($LASTEXITCODE -ne 0) { throw } ; Write-Ok "Docker daemon running" } catch {
        Write-Err "Docker daemon not running. Open Docker Desktop and wait for Running."; exit 1
    }
    if (-not (Test-Path "docker-compose.prod.yml")) { Write-Err "docker-compose.prod.yml not found"; exit 1 }
    $envPath = Join-Path $ProjectRoot ".env"
    $envExample = Join-Path $ProjectRoot ".env.example"
    if (-not (Test-Path $envPath)) {
        if (Test-Path $envExample) { Copy-Item $envExample $envPath; Write-Ok ".env created from .env.example" }
    } else { Write-Ok ".env already exists" }
    $envContent = Get-Content $envPath -Raw -ErrorAction SilentlyContinue
    if ($envContent -match "SECRET_KEY=change-me" -or $envContent -notmatch "SECRET_KEY=") {
        Write-Warn "Generating SECRET_KEY..."
        $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create(); $b = New-Object byte[] 32; $rng.GetBytes($b); $s = -join ($b | ForEach-Object { $_.ToString("x2") })
        (Get-Content $envPath) -replace "^SECRET_KEY=.*", "SECRET_KEY=$s" | Set-Content $envPath -Encoding UTF8
        Write-Ok "SECRET_KEY generated"
    }
    Write-Info "Validating compose..."
    docker compose -f docker-compose.prod.yml config 1>$null; if ($LASTEXITCODE -ne 0) { Write-Err "config failed"; exit 1 }
    Write-Info "Build..."
    docker compose -f docker-compose.prod.yml build; if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Info "Up..."
    docker compose -f docker-compose.prod.yml up -d; if ($LASTEXITCODE -ne 0) { exit 1 }
    Start-Sleep -Seconds 15
    docker compose -f docker-compose.prod.yml ps
    docker compose -f docker-compose.prod.yml logs --tail=100
    Write-Host "Frontend: http://localhost  Backend: http://localhost:8000/health" -ForegroundColor White
    try { Start-Process "http://localhost" } catch {}
    Write-Ok "Production started!"
    exit 0
}

# --- QUICK START (SQLite, no Docker) ---
Write-Host "=== Quick Start (SQLite, no Docker) ===" -ForegroundColor White

if (-not $hasNode) { Write-Err "Node.js not found: https://nodejs.org/"; exit 1 }
if (-not $hasPython) { Write-Err "Python not found: https://www.python.org/downloads/"; exit 1 }
Write-Ok "Node and Python found"

foreach ($p in @("backend", "frontend", ".env.example")) {
    if (-not (Test-Path $p)) { Write-Err "Not found $p"; exit 1 }
}

$envPath = Join-Path $ProjectRoot ".env"
$envExample = Join-Path $ProjectRoot ".env.example"
if (-not (Test-Path $envPath)) {
    Copy-Item $envExample $envPath
    Write-Ok ".env created"
    $c = Get-Content $envPath -Raw
    $c = $c -replace "DATABASE_URL=.*", "DATABASE_URL=sqlite:///./dev_bailanysta.db"
    Set-Content $envPath $c -Encoding UTF8
} else {
    Write-Ok ".env already exists - not overwriting"
}
$envContent = Get-Content $envPath -Raw
if ($envContent -match "SECRET_KEY=change-me") {
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create(); $b = New-Object byte[] 32; $rng.GetBytes($b); $s = -join ($b | ForEach-Object { $_.ToString("x2") })
    (Get-Content $envPath) -replace "SECRET_KEY=change-me.*", "SECRET_KEY=$s" | Set-Content $envPath -Encoding UTF8
    Write-Ok "SECRET_KEY generated"
}

Write-Info "Creating SQLite DB..."
$env:DATABASE_URL="sqlite:///./dev_bailanysta.db"
$env:SECRET_KEY="dev-secret-key-not-for-production-32chars-1234567890ab"
Set-Location "$ProjectRoot\backend"
# Use temp python file in backend folder to ensure app import works
$pyFile = Join-Path "$ProjectRoot\backend" "bailanysta_init_db.py"
Set-Content -LiteralPath $pyFile -Value "from app.database.base import Base`nimport app.models`nfrom sqlalchemy import create_engine`ne=create_engine('sqlite:///./dev_bailanysta.db')`nBase.metadata.create_all(bind=e)`nprint('DB ready')" -Encoding UTF8
python $pyFile
if ($LASTEXITCODE -ne 0) { Write-Err "DB creation failed"; exit 1 }
Write-Ok "SQLite DB ready: backend/dev_bailanysta.db"
Remove-Item $pyFile -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "C:\Users\lueex\Desktop\Bailanysta\backend\.venv" -ErrorAction SilentlyContinue)) {
    Write-Info "Installing backend deps (pip)..."
    python -m pip install -r requirements.txt --quiet
    if ($LASTEXITCODE -ne 0) { Write-Warn "pip install warnings, continuing" }
}

Set-Location "$ProjectRoot\frontend"
if (-not (Test-Path "node_modules")) {
    Write-Info "Installing frontend deps (npm ci)..."
    npm ci
    if ($LASTEXITCODE -ne 0) { npm install }
}

Write-Info "Starting backend (uvicorn)..."
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { try { Stop-Process -Id $_.OwningProcess -Force } catch {} }
Start-Sleep -Seconds 1
$env:DATABASE_URL="sqlite:///./dev_bailanysta.db"
$env:SECRET_KEY="dev-secret-key-not-for-production-32chars-1234567890ab"
Start-Process -FilePath "cmd" -ArgumentList '/c', 'set DATABASE_URL=sqlite:///./dev_bailanysta.db && set SECRET_KEY=dev-secret-key-not-for-production-32chars-1234567890ab && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info > uvicorn.log 2>&1' -WorkingDirectory "$ProjectRoot\backend" -WindowStyle Hidden
Start-Sleep -Seconds 5
try { $r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 5; Write-Ok "Backend health $($r.StatusCode) $($r.Content)" } catch { Write-Warn "Backend health not yet, waiting..."; Start-Sleep -Seconds 3 }

Write-Info "Starting frontend (vite)..."
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { try { Stop-Process -Id $_.OwningProcess -Force } catch {} }
Start-Sleep -Seconds 1
Start-Process -FilePath "cmd" -ArgumentList '/c', 'npm run dev -- --host 0.0.0.0 --port 5173 > frontend.log 2>&1' -WorkingDirectory "$ProjectRoot\frontend" -WindowStyle Hidden
Start-Sleep -Seconds 8
try { $r = Invoke-WebRequest -Uri "http://127.0.0.1:5173" -UseBasicParsing -TimeoutSec 5; Write-Ok "Frontend $($r.StatusCode) len $($r.Content.Length)" } catch { Write-Warn "Frontend not yet" }

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Bailanysta started (Quick Start)!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host " Frontend: http://localhost:5173" -ForegroundColor White
Write-Host " Backend:  http://localhost:8000" -ForegroundColor White
Write-Host " Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host " Health:   http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host " Try:" -ForegroundColor Gray
Write-Host "  1. Click 'Enter demo' on /login" -ForegroundColor White
Write-Host "  2. Or register: browser_test / test@example.com / Secret123!" -ForegroundColor White
Write-Host ""

try { Start-Process "http://localhost:5173" } catch {}
Write-Ok "Done. If you see Bailanysta - it works."
