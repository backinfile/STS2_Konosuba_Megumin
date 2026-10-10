param([switch]$SkipBridge, [ValidatePattern('^actions-v[0-9]+$')][string]$Actions = 'actions-v9')
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$configPath = Join-Path $repo '.local/lab.json'
if (-not (Test-Path -LiteralPath $configPath)) { & (Join-Path $PSScriptRoot 'prepare-lab.ps1') }
$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$output = Join-Path $repo 'dist/MeguminMod'
dotnet build (Join-Path $repo 'mod/MeguminMod.csproj') -c Release -o $output "-p:STS2GameDir=$($config.GameDir)" "-p:BaseLibDir=$($config.BaseLibDir)"
if ($LASTEXITCODE -ne 0) { throw 'Megumin mod build failed.' }
Copy-Item -LiteralPath (Join-Path $repo 'mod/MeguminMod.json') -Destination $output -Force
foreach ($name in @('MeguminMod.deps.json','MeguminMod.runtimeconfig.json')) {
    $file = Join-Path $output $name
    if (Test-Path -LiteralPath $file) { Remove-Item -LiteralPath $file }
}
$animation = Join-Path $output 'animation'
New-Item -ItemType Directory -Path $animation -Force | Out-Null
$export = Join-Path $repo "art/megumin-quartet-spine/$Actions/export"
foreach ($source in Get-ChildItem -LiteralPath $export -File) {
    if ($source.Extension -in @('.png','.atlas')) { Copy-Item -LiteralPath $source.FullName -Destination $animation -Force }
}
Copy-Item -LiteralPath (Join-Path $export 'megumin.json') -Destination (Join-Path $animation 'megumin.spine-json') -Force
if (Test-Path -LiteralPath (Join-Path $animation 'megumin.json')) { Remove-Item -LiteralPath (Join-Path $animation 'megumin.json') }
$modDest = Join-Path $config.Runtime 'mods/MeguminMod'
New-Item -ItemType Directory -Path $modDest -Force | Out-Null
Copy-Item -Path (Join-Path $output '*') -Destination $modDest -Recurse -Force
foreach ($name in @('MeguminMod.deps.json','MeguminMod.runtimeconfig.json','animation/megumin.json')) {
    $file = Join-Path $modDest $name
    if (Test-Path -LiteralPath $file) { Remove-Item -LiteralPath $file }
}
if (-not $SkipBridge) {
    $bridge = Join-Path $config.Runtime 'mods/KarenSTS2MCP'
    dotnet build (Join-Path $repo 'tools/vendor/STS2_Mcp/KarenSTS2MCP.csproj') -c Release -o $bridge "-p:STS2GameDir=$($config.GameDir)"
    if ($LASTEXITCODE -ne 0) { throw 'MCP bridge build failed.' }
    $deps = Join-Path $bridge 'KarenSTS2MCP.deps.json'
    if (Test-Path -LiteralPath $deps) { Remove-Item -LiteralPath $deps }
    Copy-Item -LiteralPath (Join-Path $repo 'tools/vendor/STS2_Mcp/mod_manifest.json') -Destination (Join-Path $bridge 'KarenSTS2MCP.json') -Force
    @{port=15528; muted=$true; skip_tutorial=$true; skip_first_prompt=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $bridge 'KarenSTS2MCP.conf') -Encoding utf8
}
Write-Output "Built and installed to the project lab: $modDest"
