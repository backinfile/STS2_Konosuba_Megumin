param(
    [string]$GameDir = 'D:/App/Stream/steamapps/common/Slay the Spire 2',
    [string]$BaseLibDir = 'D:/App/Stream/steamapps/workshop/content/2868840/3737335127/BaseLib',
    [string]$McpSource = (Join-Path $PSScriptRoot 'vendor/STS2_Mcp')
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$lab = Join-Path $repo '.local'
$runtime = Join-Path $lab 'game'
foreach ($required in @((Join-Path $GameDir 'SlayTheSpire2.exe'), (Join-Path $BaseLibDir 'BaseLib.dll'), (Join-Path $McpSource 'KarenSTS2MCP.csproj'))) {
    if (-not (Test-Path -LiteralPath $required)) { throw "Missing dependency: $required" }
}
New-Item -ItemType Directory -Path $runtime -Force | Out-Null
# Link immutable game files; configs, mods and saves are separate ordinary files.
foreach ($source in Get-ChildItem -LiteralPath $GameDir -File) {
    if ($source.Extension -notin @('.exe','.dll','.pck') -and $source.Name -ne 'release_info.json') { continue }
    $destination = Join-Path $runtime $source.Name
    if (-not (Test-Path -LiteralPath $destination)) {
        New-Item -ItemType HardLink -Path $destination -Target $source.FullName | Out-Null
    }
}
$dataName = 'data_sts2_windows_x86_64'
foreach ($source in Get-ChildItem -LiteralPath (Join-Path $GameDir $dataName) -File -Recurse) {
    $relative = [IO.Path]::GetRelativePath($GameDir, $source.FullName)
    $destination = Join-Path $runtime $relative
    New-Item -ItemType Directory -Path (Split-Path $destination -Parent) -Force | Out-Null
    if (-not (Test-Path -LiteralPath $destination)) {
        New-Item -ItemType HardLink -Path $destination -Target $source.FullName | Out-Null
    }
}
$baseDest = Join-Path $runtime 'mods/BaseLib'
New-Item -ItemType Directory -Path $baseDest -Force | Out-Null
foreach ($name in @('BaseLib.dll','BaseLib.pck','BaseLib.json')) { Copy-Item -LiteralPath (Join-Path $BaseLibDir $name) -Destination $baseDest -Force }
$bridge = Join-Path $repo 'tools/vendor/STS2_Mcp'
if ([IO.Path]::GetFullPath($McpSource) -ne [IO.Path]::GetFullPath($bridge)) {
New-Item -ItemType Directory -Path $bridge -Force | Out-Null
foreach ($source in Get-ChildItem -LiteralPath $McpSource -File) {
    if ($source.Extension -eq '.cs' -or $source.Name -in @('KarenSTS2MCP.csproj','LICENSE','mod_manifest.json')) {
        Copy-Item -LiteralPath $source.FullName -Destination $bridge -Force
    }
}
$mcpFolder = Join-Path $bridge 'mcp'
New-Item -ItemType Directory -Path $mcpFolder -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $McpSource 'mcp/server.py') -Destination $mcpFolder -Force
$sourceRevision = git -C $McpSource rev-parse HEAD
@{source=$McpSource; revision=$sourceRevision; imported_at=(Get-Date -Format o); license='MIT'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $bridge 'PROVENANCE.json') -Encoding utf8
}
$savePath = (Join-Path $lab 'userdata').Replace('\','/')
New-Item -ItemType Directory -Path $savePath -Force | Out-Null
$saveName = 'MeguminModLab-STS2_Konosuba_Megumin'
$saveLink = Join-Path ([System.Environment]::GetFolderPath('ApplicationData')) $saveName
if (Test-Path -LiteralPath $saveLink) {
    $existingLink = Get-Item -LiteralPath $saveLink
    if ($existingLink.LinkType -ne 'Junction' -or [IO.Path]::GetFullPath($existingLink.Target) -ne [IO.Path]::GetFullPath($savePath)) {
        throw "Lab save junction already exists with another target: $saveLink"
    }
} else { New-Item -ItemType Junction -Path $saveLink -Target $savePath | Out-Null }
@"
[application]
config/use_custom_user_dir=true
config/custom_user_dir_name="$saveName"
[display]
window/size/mode=1
window/size/viewport_width=1920
window/size/viewport_height=1080
window/size/window_width_override=1280
window/size/window_height_override=720
window/size/no_focus=true
[audio]
driver/enable_input=false
"@ | Set-Content -LiteralPath (Join-Path $runtime 'override.cfg') -Encoding utf8
@{GameDir=$GameDir; BaseLibDir=$baseDest; Runtime=$runtime; UserData=$savePath; McpPort=15528; LabPort=15529} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $lab 'lab.json') -Encoding utf8
Write-Output "Lab ready: $runtime"
Write-Output "Independent save directory: $savePath"
