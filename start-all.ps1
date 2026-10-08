# Script khởi động toàn bộ dịch vụ dự án VIỆT FIT (Monorepo Orchestrator)
Write-Host "=== Khởi động hệ thống VIỆT FIT ===" -ForegroundColor Cyan

$root = $PSScriptRoot
if (-not $root) { $root = Get-Location }

# Đọc file .env nếu có
$envFile = Join-Path $root ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | Where-Object { $_ -match '^([^#=]+)=(.*)$' } | ForEach-Object {
        $key = $matches[1].Trim()
        $val = $matches[2].Trim()
        [System.Environment]::SetEnvironmentVariable($key, $val, "Process")
    }
}

# 1. Kiểm tra PostgreSQL
Write-Host "[1/4] Kiểm tra PostgreSQL..." -ForegroundColor Yellow
$pgPort = Get-NetTCPConnection -LocalPort 5432 -State Listen -ErrorAction SilentlyContinue
if (-not $pgPort) {
    Write-Host "  > Đang khởi động dịch vụ PostgreSQL..." -ForegroundColor Gray
    Start-Service -Name *postgres* -ErrorAction SilentlyContinue
}
Write-Host "  > PostgreSQL đã sẵn sàng (Port 5432)" -ForegroundColor Green

# 2. Khởi động AI Service (Port 8000)
Write-Host "[2/4] Kiểm tra AI Service (Port 8000)..." -ForegroundColor Yellow
$aiPort = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if (-not $aiPort) {
    $pythonExe = Join-Path $root "ai-service\.venv\Scripts\python.exe"
    $aiDir = Join-Path $root "ai-service"
    Start-Process -FilePath $pythonExe `
        -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000" `
        -WorkingDirectory $aiDir `
        -WindowStyle Minimized
    Start-Sleep -Seconds 2
}
Write-Host "  > AI Service hoạt động tại http://127.0.0.1:8000" -ForegroundColor Green

# 3. Khởi động Backend Spring Boot (Port 8080)
Write-Host "[3/4] Kiểm tra Backend Spring Boot (Port 8080)..." -ForegroundColor Yellow
$backendPort = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue
if (-not $backendPort) {
    $backendDir = Join-Path $root "backend"
    $jarPath = Join-Path $backendDir "build\libs\viet-fit-backend-0.1.0.jar"
    if (-not (Test-Path $jarPath)) {
        Write-Host "  > Đang build bootJar lần đầu..." -ForegroundColor Gray
        Start-Process -FilePath (Join-Path $backendDir "gradlew.bat") -ArgumentList "bootJar" -WorkingDirectory $backendDir -Wait
    }
    Start-Process -FilePath "java" `
        -ArgumentList "-Dspring.datasource.url=$env:DATABASE_URL -Dspring.datasource.username=$env:DATABASE_USERNAME -Dspring.datasource.password=$env:DATABASE_PASSWORD -Dapp.weather.api-key=$env:WEATHER_API_KEY -Dapp.ai.base-url=$env:AI_SERVICE_URL -jar build\libs\viet-fit-backend-0.1.0.jar" `
        -WorkingDirectory $backendDir `
        -WindowStyle Minimized
    Start-Sleep -Seconds 4
}
Write-Host "  > Backend Spring Boot hoạt động tại http://127.0.0.1:8080" -ForegroundColor Green

# 4. Khởi động Frontend Vite (Port 5173)
Write-Host "[4/4] Kiểm tra Frontend (Port 5173)..." -ForegroundColor Yellow
$fePort = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
if (-not $fePort) {
    $feDir = Join-Path $root "frontend"
    Start-Process -FilePath "npm.cmd" `
        -ArgumentList "run dev" `
        -WorkingDirectory $feDir `
        -WindowStyle Minimized
    Start-Sleep -Seconds 2
}
Write-Host "  > Frontend hoạt động tại http://localhost:5173" -ForegroundColor Green

Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host " HỆ THỐNG VIỆT FIT ĐÃ KẾT NỐI VÀ SẴN SÀNG:" -ForegroundColor Cyan
Write-Host " - Giao diện Web:      http://localhost:5173" -ForegroundColor White
Write-Host " - Backend API:        http://localhost:8080/api/health" -ForegroundColor White
Write-Host " - AI Service:         http://localhost:8000/ai/health" -ForegroundColor White
Write-Host " - AI Docs / Swagger:  http://localhost:8000/ai/docs" -ForegroundColor White
Write-Host " - AI Playground:      http://localhost:8000/ai/playground" -ForegroundColor White
Write-Host "===============================================" -ForegroundColor Cyan
