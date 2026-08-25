# ====================================================================
# AI Consensus Arena (SIH Super-Architecture) - Startup Script
# ====================================================================

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Starting AI Consensus Arena (Multi-Model SIH Gauntlet)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$RootPath = $PSScriptRoot
$BackendPath = Join-Path $RootPath "multi-ai-debate\backend"
$FrontendPath = Join-Path $RootPath "multi-ai-debate\frontend"

if (-not (Test-Path $BackendPath)) {
    $BackendPath = Join-Path $RootPath "backend"
    $FrontendPath = Join-Path $RootPath "frontend"
}

Write-Host ""
Write-Host "[1/4] Checking environment & freeing ports..." -ForegroundColor Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Node.js / npm is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# Free ports 8000 and 3000 if occupied by previous runs
try {
    $p8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    if ($p8000) { Stop-Process -Id $p8000 -Force -ErrorAction SilentlyContinue }
    $p3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    if ($p3000) { Stop-Process -Id $p3000 -Force -ErrorAction SilentlyContinue }
} catch {}

Write-Host "  OK: Environment ready & ports clean." -ForegroundColor Green

Write-Host ""
Write-Host "[2/4] Launching Backend Server on http://localhost:8000..." -ForegroundColor Yellow
$BackendCmd = "Set-Location -Path '$BackendPath'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$BackendCmd" -WindowStyle Normal

Write-Host ""
Write-Host "[3/4] Launching Frontend Server on http://localhost:3000..." -ForegroundColor Yellow
$FrontendCmd = "Set-Location -Path '$FrontendPath'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$FrontendCmd" -WindowStyle Normal

Write-Host ""
Write-Host "[4/4] Waiting 4 seconds for servers to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 4

Write-Host ""
Write-Host "Opening AI Consensus Arena UI..." -ForegroundColor Green
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host " BOTH SERVERS ARE RUNNING!" -ForegroundColor Green
Write-Host "    - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "    - Backend API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Green
Write-Host "Press any key to close this launcher window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
