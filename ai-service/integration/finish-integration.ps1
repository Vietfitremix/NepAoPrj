$ErrorActionPreference = 'Stop'
$taskWorkspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$taskPatch = Join-Path $PSScriptRoot 'integration.patch'
$taskManifest = Get-Content -LiteralPath (Join-Path $taskWorkspace 'frontend/tools/import-manifest.json') -Raw | ConvertFrom-Json
if ($taskManifest.copiedFiles -ne 169) { throw 'Incomplete source migration.' }
foreach ($taskEntry in $taskManifest.files) {
    $taskCopy = [IO.Path]::GetFullPath((Join-Path $taskWorkspace $taskEntry.target))
    if (-not $taskCopy.StartsWith($taskWorkspace + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Copy path outside workspace.' }
    if ((Get-FileHash -LiteralPath $taskCopy -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskEntry.targetSha256) {
        throw "Copied file was changed or lost: $taskCopy. Keep NepAoPrj until verified."
    }
}
Push-Location $taskWorkspace
try {
    if (Test-Path -LiteralPath (Join-Path $taskWorkspace 'NepAoPrj')) {
        & node frontend/tools/verify-import.cjs
        if ($LASTEXITCODE -ne 0) { throw 'Source verification failed; no source folders deleted.' }
    }
    $taskAlreadyApplied = $true
    Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'preview') -File -Recurse | ForEach-Object {
        $taskRelativeFile = $_.FullName.Substring((Join-Path $PSScriptRoot 'preview').Length + 1)
        $taskAppliedFile = Join-Path $taskWorkspace $taskRelativeFile
        if (-not (Test-Path -LiteralPath $taskAppliedFile)) { $taskAlreadyApplied = $false }
        elseif ([IO.File]::ReadAllText($_.FullName).Replace("`r`n", "`n") -ne [IO.File]::ReadAllText($taskAppliedFile).Replace("`r`n", "`n")) { $taskAlreadyApplied = $false }
    }
    if (-not $taskAlreadyApplied) {
        & git apply --check --ignore-space-change $taskPatch
        if ($LASTEXITCODE -ne 0) { throw 'Patch differs from current files; no source folders deleted.' }
        & git apply --ignore-space-change $taskPatch
        if ($LASTEXITCODE -ne 0) { throw 'Patch application failed; no source folders deleted.' }
    } else {
        Write-Output 'Integration patch already applied; continuing verification.'
    }
    Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'preview') -File -Recurse | ForEach-Object {
        $taskRelativeFile = $_.FullName.Substring((Join-Path $PSScriptRoot 'preview').Length + 1)
        $taskAppliedFile = Join-Path $taskWorkspace $taskRelativeFile
        $taskExpectedContent = [IO.File]::ReadAllText($_.FullName).Replace("`r`n", "`n")
        $taskAppliedContent = [IO.File]::ReadAllText($taskAppliedFile).Replace("`r`n", "`n")
        if ($taskExpectedContent -ne $taskAppliedContent) { throw "Patch write did not succeed: $taskAppliedFile. Source folders retained." }
    }
    Push-Location (Join-Path $taskWorkspace 'frontend')
    try {
        & npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed; source folders retained.' }
        & npm.cmd test
        if ($LASTEXITCODE -ne 0) { throw 'Frontend tests failed; source folders retained.' }
    } finally { Pop-Location }
    foreach ($taskRelative in @('NepAoPrj', 'backend/ai-service')) {
        $taskTarget = [IO.Path]::GetFullPath((Join-Path $taskWorkspace $taskRelative))
        $taskExpected = if ($taskRelative -eq 'NepAoPrj') { Join-Path $taskWorkspace 'NepAoPrj' } else { Join-Path $taskWorkspace 'backend\ai-service' }
        if ($taskTarget -ne $taskExpected -or -not $taskTarget.StartsWith($taskWorkspace + '\', [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Unexpected deletion target.'
        }
        if (Test-Path -LiteralPath $taskTarget) { Remove-Item -LiteralPath $taskTarget -Recurse -Force }
    }
    $taskDirectories = @(Get-ChildItem -LiteralPath $taskWorkspace -Directory -Force | Where-Object { -not $_.Name.StartsWith('.') } | Select-Object -ExpandProperty Name)
    if (@(Compare-Object @('ai-service','backend','frontend') $taskDirectories).Count) {
        throw 'Additional root directories remain; inspect manually.'
    }
    Write-Output 'Done: only frontend, backend and ai-service remain. Start services following README.md in this folder.'
} finally { Pop-Location }
