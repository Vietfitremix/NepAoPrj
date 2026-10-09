$ErrorActionPreference = 'Stop'

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "    VIET-FIT / NẾP ÁO DOCKER DEPLOY       " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$composeFile = if (Test-Path "docker-compose.prod.yml") { "docker-compose.prod.yml" } else { "docker-compose.yml" }

if (-not (Test-Path ".env")) {
    Write-Warning ".env not found! Copying from .env.example..."
    Copy-Item ".env.example" ".env"
}

Write-Host "[1/3] Building & starting containers..." -ForegroundColor Yellow
docker compose -f $composeFile up -d --build --remove-orphans

Write-Host "[2/3] Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

function Test-Endpoint($url, $name) {
    Write-Host "Testing $name at $url..." -NoNewline
    for ($i = 1; $i -le 10; $i++) {
        try {
            $res = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($res.StatusCode -eq 200) {
                Write-Host " OK!" -ForegroundColor Green
                return $true
            }
        } catch { }
        Start-Sleep -Seconds 2
    }
    Write-Host " TIMEOUT/FAIL" -ForegroundColor Red
    return $false
}

Test-Endpoint "http://localhost:8080/api/health" "Backend"
Test-Endpoint "http://localhost:8000/ai/health" "AI Service"
Test-Endpoint "http://localhost/nginx-health" "Frontend"

Write-Host "Deploy complete! Open http://localhost in browser." -ForegroundColor Green
