$ErrorActionPreference = 'Stop'
$taskWorkspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
foreach ($taskCommand in @('docker', 'node', 'npm.cmd', 'git')) {
    if (-not (Get-Command $taskCommand -ErrorAction SilentlyContinue)) {
        throw "Missing $taskCommand. Install Docker Desktop (and start it), Node.js and Git, then rerun this script."
    }
}
& docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Docker Desktop is not running.' }
& docker compose version
if ($LASTEXITCODE -ne 0) { throw 'Docker Compose is unavailable.' }

# Complete source migration and verify the frontend before starting services.
& (Join-Path $PSScriptRoot 'finish-integration.ps1')

Push-Location $taskWorkspace
try {
    $taskAssetTest = Join-Path $taskWorkspace 'backend/src/test/java/com/vietphuc/remix/ApiIntegrationTest.java'
    $taskAssetTestContent = [IO.File]::ReadAllText($taskAssetTest)
    $taskOldAssetAssertion = '.andExpect(jsonPath("$.assets",hasSize(0)));'
    if ($taskAssetTestContent.Contains($taskOldAssetAssertion)) {
        & git apply --check --unidiff-zero (Join-Path $PSScriptRoot 'fix-asset-test.patch')
        if ($LASTEXITCODE -ne 0) { throw 'Asset test patch does not match current backend.' }
        & git apply --unidiff-zero (Join-Path $PSScriptRoot 'fix-asset-test.patch')
        if ($LASTEXITCODE -ne 0) { throw 'Cannot update backend asset test.' }
    }
} finally { Pop-Location }

Push-Location (Join-Path $taskWorkspace 'backend')
try {
    if (-not (Test-Path -LiteralPath '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
    & docker compose build ai backend
    if ($LASTEXITCODE -ne 0) { throw 'Docker image build failed. The build error is printed above this message.' }
    & docker compose up --no-build -d postgres ai backend
    if ($LASTEXITCODE -ne 0) {
        & docker compose ps -a
        & docker compose logs --tail=100 postgres ai backend
        throw 'Container startup failed. Inspect the Docker error and container logs printed above.'
    }
    $taskBackendReady = $false
    for ($taskAttempt = 0; $taskAttempt -lt 60; $taskAttempt++) {
        try {
            $taskHealth = Invoke-RestMethod 'http://127.0.0.1:8080/api/health' -TimeoutSec 2
            if ($taskHealth.status -eq 'UP') { $taskBackendReady = $true; break }
        } catch { }
        Start-Sleep -Seconds 2
    }
    if (-not $taskBackendReady) { throw 'Backend health check failed. Run: cd backend; docker compose logs backend ai' }
    & docker compose exec -T ai python -c 'import sys,urllib.request; urllib.request.urlopen(sys.argv[1],timeout=5)' http://127.0.0.1:8000/ai/openapi.json
    if ($LASTEXITCODE -ne 0) { throw 'AI service health check failed. Inspect docker compose logs ai.' }
} finally { Pop-Location }

Write-Output 'Backend ready: http://localhost:8080/api/health'
Write-Output 'AI service ready inside Docker at http://ai:8000.'
Write-Output 'Frontend: http://localhost:5173. Keep this terminal open.'
Write-Output 'Set WEATHER_API_KEY in backend/.env for weather and recommendations; Gemini is optional.'
Push-Location (Join-Path $taskWorkspace 'frontend')
try {
    & npm.cmd run dev -- --host 127.0.0.1 --port 5173 --strictPort
    if ($LASTEXITCODE -ne 0) { throw 'Frontend startup failed.' }
} finally { Pop-Location }
