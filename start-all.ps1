$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$logDir = Join-Path $root '.tools'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

# Load local settings without putting credentials on command lines.
$envFile = Join-Path $root '.env'
if (Test-Path -LiteralPath $envFile) {
    foreach ($line in Get-Content -LiteralPath $envFile -Encoding UTF8) {
        if ($line -match '^\s*([^#=\s]+)\s*=(.*)$') {
            $key = $matches[1]
            $value = $matches[2].Trim()
            if ($value.Length -ge 2 -and (($value.StartsWith('"') -and $value.EndsWith('"')) -or
                ($value.StartsWith("'") -and $value.EndsWith("'")))) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            [Environment]::SetEnvironmentVariable($key, $value, 'Process')
        }
    }
}

function Test-ListeningPort([int]$Port) {
    return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

function Wait-Ready([string]$Url, [string]$Name, $Process = $null) {
    $deadline = (Get-Date).AddSeconds(60)
    do {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) { return }
        } catch { }
        if ($null -ne $Process -and $Process.HasExited) {
            throw "$Name exited before becoming ready. See logs in $logDir."
        }
        Start-Sleep -Milliseconds 400
    } while ((Get-Date) -lt $deadline)
    throw "$Name did not become ready at $Url. See logs in $logDir."
}

Write-Host '[1/4] Checking PostgreSQL...' -ForegroundColor Cyan
if (-not (Test-ListeningPort 5432)) {
    $services = Get-Service -Name '*postgres*' -ErrorAction SilentlyContinue
    if (-not $services) { throw 'PostgreSQL is not running. Start the database on port 5432 first.' }
    $services | Where-Object Status -ne 'Running' | Start-Service
}
if (-not (Test-ListeningPort 5432)) { throw 'PostgreSQL is not listening on port 5432.' }

Write-Host '[2/4] Starting Spring backend...' -ForegroundColor Cyan
$backendProcess = $null
if (-not (Test-ListeningPort 8080)) {
    $backendDir = Join-Path $root 'backend'
    # Incremental build also picks up changes after a merge.
    Push-Location $backendDir
    try {
        & '.\gradlew.bat' bootJar --console=plain
        if ($LASTEXITCODE -ne 0) { throw 'Backend build failed.' }
    } finally { Pop-Location }
    $javaExe = (Get-Command java -ErrorAction Stop).Source
    $backendProcess = Start-Process -FilePath $javaExe `
        -ArgumentList '-jar build\libs\viet-fit-backend-0.1.0.jar' `
        -WorkingDirectory $backendDir -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $logDir 'backend.stdout.log') `
        -RedirectStandardError (Join-Path $logDir 'backend.stderr.log')
}
Wait-Ready 'http://127.0.0.1:8080/api/health' 'Spring backend' $backendProcess

# Import unchanged asset bytes after Flyway has created the data tables.
Write-Host 'Importing/verifying database assets...' -ForegroundColor Cyan
& (Join-Path $root 'ai-service\.venv\Scripts\python.exe') -X utf8 (Join-Path $root 'backend\import_data.py') --assets
if ($LASTEXITCODE -ne 0) { throw 'Asset import failed; see the import output above.' }

Write-Host '[3/4] Starting AI service...' -ForegroundColor Cyan
$aiProcess = $null
if (-not (Test-ListeningPort 8000)) {
    # Spring's jdbc: URL is not a Python/PostgreSQL connection string.
    # Let AI load its own DATABASE_URL from ai-service/.env instead.
    $springDatabaseUrl = [Environment]::GetEnvironmentVariable('DATABASE_URL', 'Process')
    $previousCatalogUrl = [Environment]::GetEnvironmentVariable('CATALOG_DATABASE_URL', 'Process')
    try {
        if (-not $previousCatalogUrl) {
            $databaseUri = [uri]($springDatabaseUrl -replace '^jdbc:', '')
            $encodedUser = [uri]::EscapeDataString($env:DATABASE_USERNAME)
            $encodedPassword = [uri]::EscapeDataString($env:DATABASE_PASSWORD)
            $catalogUrl = "postgresql://${encodedUser}:${encodedPassword}@$($databaseUri.Authority)$($databaseUri.AbsolutePath)"
            [Environment]::SetEnvironmentVariable('CATALOG_DATABASE_URL', $catalogUrl, 'Process')
        }
        [Environment]::SetEnvironmentVariable('DATABASE_URL', $null, 'Process')
        $aiProcess = Start-Process -FilePath (Join-Path $root 'ai-service\.venv\Scripts\python.exe') `
            -ArgumentList '-X utf8 -m uvicorn app.main:app --loop app.core.event_loop:selector_loop_factory --host 127.0.0.1 --port 8000' `
            -WorkingDirectory (Join-Path $root 'ai-service') -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput (Join-Path $logDir 'ai.stdout.log') `
            -RedirectStandardError (Join-Path $logDir 'ai.stderr.log')
    } finally {
        [Environment]::SetEnvironmentVariable('DATABASE_URL', $springDatabaseUrl, 'Process')
        [Environment]::SetEnvironmentVariable('CATALOG_DATABASE_URL', $previousCatalogUrl, 'Process')
    }
}
Wait-Ready 'http://127.0.0.1:8000/ai/health' 'AI service' $aiProcess

Write-Host '[4/4] Starting frontend...' -ForegroundColor Cyan
$frontendProcess = $null
if (-not (Test-ListeningPort 5173)) {
    $npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
    $npmExe = if ($npmCommand) { $npmCommand.Source } else { Join-Path $env:ProgramFiles 'nodejs\npm.cmd' }
    if (-not (Test-Path -LiteralPath $npmExe)) { throw 'Node.js/npm is not installed.' }
    $env:PATH = "$(Split-Path -Parent $npmExe);$env:PATH"
    $frontendProcess = Start-Process -FilePath $npmExe `
        -ArgumentList 'run dev -- --port 5173 --strictPort' `
        -WorkingDirectory (Join-Path $root 'frontend') -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $logDir 'frontend.stdout.log') `
        -RedirectStandardError (Join-Path $logDir 'frontend.stderr.log')
}
Wait-Ready 'http://127.0.0.1:5173' 'Frontend' $frontendProcess
# Verify the same /api route that the browser uses.
Wait-Ready 'http://127.0.0.1:5173/api/health' 'Frontend API proxy'

Write-Host 'Ready: http://localhost:5173' -ForegroundColor Green
Write-Host 'Backend: http://localhost:8080/api/health'
Write-Host 'AI: http://localhost:8000/ai/health'
Write-Host "Logs: $logDir"
