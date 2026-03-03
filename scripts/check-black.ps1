Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

$packageDirs = @(
    "packages/mini-arcade",
    "packages/mini-arcade-core",
    "packages/mini-arcade-pygame-backend",
    "packages/mini-arcade-native-backend"
)

& $python -m black --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "black is not available in the selected Python environment."
}

$failed = @()

foreach ($packageDir in $packageDirs) {
    $packagePath = Join-Path $repoRoot $packageDir
    if (-not (Test-Path $packagePath)) {
        throw "Package path not found: $packagePath"
    }

    Write-Host "==> black --check . ($packageDir)"
    Push-Location $packagePath
    try {
        & $python -m black --check .
        if ($LASTEXITCODE -ne 0) {
            $failed += $packageDir
        }
    }
    finally {
        Pop-Location
    }
}

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "black check failed for:"
    $failed | ForEach-Object { Write-Host " - $_" }
    exit 1
}

Write-Host ""
Write-Host "All package black checks passed."
