param([switch]$Headless, [switch]$Build, [switch]$Visible)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
if ($Build) { & (Join-Path $PSScriptRoot 'build-mod.ps1') }
$config = Get-Content -LiteralPath (Join-Path $repo '.local/lab.json') -Raw | ConvertFrom-Json
$exe = Join-Path $config.Runtime 'SlayTheSpire2.exe'
$existing = Get-Process -Name SlayTheSpire2 -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $exe }
if ($existing) { Write-Output "Project lab already running: $($existing.Id)"; return }
# Seed only this independent test profile. The game's regular saves are untouched.
$saveFolder = Join-Path $config.UserData 'default/1'
New-Item -ItemType Directory -Path $saveFolder -Force | Out-Null
$settingsPath = Join-Path $saveFolder 'settings.save'
if (-not (Test-Path -LiteralPath $settingsPath)) {
    @{schema_version=5; language='zhs'; fullscreen=$false; volume_master=0; volume_bgm=0; skip_intro_logo=$true; seen_ea_disclaimer=$true; limit_fps_in_background=$false; mod_settings=@{mods_enabled=$true;mod_list=@()}} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $settingsPath -Encoding utf8
}
$oldLab = $env:MEGUMIN_LAB
$oldVisible = $env:MEGUMIN_LAB_VISIBLE
try {
    $env:MEGUMIN_LAB = '1'
    $env:MEGUMIN_LAB_VISIBLE = if ($Visible) { '1' } else { '0' }
    $arguments = @('--force-steam','off','--rendering-method','gl_compatibility','--audio-driver','Dummy','--log-file',(Join-Path $repo '.local/game.log'))
    if ($Headless) { $arguments += '--headless' }
    $quotedArguments = $arguments | ForEach-Object { '"' + $_.Replace('"','\"') + '"' }
    $windowStyle = if ($Visible) { 'Normal' } else { 'Hidden' }
    $process = Start-Process -FilePath $exe -ArgumentList $quotedArguments -WorkingDirectory $config.Runtime -WindowStyle $windowStyle -PassThru -RedirectStandardOutput (Join-Path $repo '.local/stdout.log') -RedirectStandardError (Join-Path $repo '.local/stderr.log')
    $process.Id | Set-Content -LiteralPath (Join-Path $repo '.local/lab.pid')
    Write-Output "Started project lab PID $($process.Id). MCP: http://127.0.0.1:15528 ; animation: http://127.0.0.1:15529"
} finally { $env:MEGUMIN_LAB = $oldLab; $env:MEGUMIN_LAB_VISIBLE = $oldVisible }
