$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$source = Join-Path $repo 'dist/MeguminMod'
if (-not (Test-Path -LiteralPath (Join-Path $source 'MeguminMod.dll'))) { throw 'Run build-mod.ps1 first.' }
Copy-Item -LiteralPath (Join-Path $repo 'docs/mod-lab.md') -Destination (Join-Path $source 'README.md') -Force
$zip = Join-Path $repo 'dist/MeguminMod-0.1.0-dev.zip'
Compress-Archive -LiteralPath $source -DestinationPath $zip -Force
Write-Output $zip
