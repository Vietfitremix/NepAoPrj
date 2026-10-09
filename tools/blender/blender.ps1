param([switch]$Render)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$blenderExe = Join-Path $projectRoot '.tools/blender/blender-4.5.3-windows-x64/blender.exe'
if (-not (Test-Path -LiteralPath $blenderExe)) {
    throw 'Blender portable is missing. See tools/blender/README.md.'
}
if ($Render) {
    & $blenderExe --background --factory-startup --python-exit-code 1 --python (Join-Path $PSScriptRoot 'create_character.py')
    if ($LASTEXITCODE -ne 0) { throw "Blender render failed: $LASTEXITCODE" }
} else {
    $scenePath = Join-Path $projectRoot 'assets/archive/blender/viet-fit-character.blend'
    if (Test-Path -LiteralPath $scenePath) {
        Start-Process -FilePath $blenderExe -ArgumentList ('"' + $scenePath + '"') -WindowStyle Hidden
    } else {
        Start-Process -FilePath $blenderExe -WindowStyle Hidden
    }
}
