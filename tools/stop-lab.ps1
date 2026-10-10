$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$config = Get-Content -LiteralPath (Join-Path $repo '.local/lab.json') -Raw | ConvertFrom-Json
$exe = [IO.Path]::GetFullPath((Join-Path $config.Runtime 'SlayTheSpire2.exe'))
$owned = @(Get-Process -Name SlayTheSpire2 -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $exe })
if (-not $owned.Count) { return }
try { Invoke-RestMethod -Uri 'http://127.0.0.1:15529/quit' -Method Post -ContentType 'application/json' -Body '{}' -TimeoutSec 3 | Out-Null } catch { }
foreach ($process in $owned) {
    if (-not $process.WaitForExit(5000)) {
        if ((Get-Process -Id $process.Id).Path -eq $exe) { Stop-Process -Id $process.Id }
    }
}
Write-Output 'Project lab stopped.'
