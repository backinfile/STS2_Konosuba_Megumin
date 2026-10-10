$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$venv = Join-Path $repo '.local/mcp-env'
$python = Join-Path $venv 'Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    py -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw 'Failed to create the local MCP environment.' }
    & $python -m pip install -r (Join-Path $PSScriptRoot 'mcp-requirements.txt') 1>&2
    if ($LASTEXITCODE -ne 0) { throw 'Failed to install MCP dependencies.' }
}
& $python (Join-Path $PSScriptRoot 'vendor/STS2_Mcp/mcp/server.py') --host 127.0.0.1 --port 15528 --no-trust-env
exit $LASTEXITCODE
