# Build the Windows NSIS installer on a Windows machine.
# Requires Python, Node.js, Rust, and Visual Studio Build Tools.
#
# Output: credit_ai_frontend\src-tauri\target\release\bundle\nsis\Kuber_*_x64-setup.exe

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "../../..")).Path
$reasoning = Join-Path $repo "reasoning_layer"
$frontend = Join-Path $repo "credit_ai_frontend"
$binaries = Join-Path $frontend "src-tauri\binaries"

Set-Location $reasoning
python -m PyInstaller reasoning_layer.spec
New-Item -ItemType Directory -Force -Path $binaries | Out-Null
Copy-Item (Join-Path $reasoning "dist\reasoning-layer.exe") (Join-Path $binaries "reasoning-layer.exe") -Force

Set-Location $frontend
npm run desktop:build:windows
