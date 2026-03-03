Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

$packages = @(
    @{ Dir = "packages/mini-arcade"; LintPath = "src/mini_arcade" },
    @{ Dir = "packages/mini-arcade-core"; LintPath = "src/mini_arcade_core" },
    @{ Dir = "packages/mini-arcade-pygame-backend"; LintPath = "src/mini_arcade_pygame_backend" },
    @{ Dir = "packages/mini-arcade-native-backend"; LintPath = "src/mini_arcade_native_backend" }
)

& $python -m pylint --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "pylint is not available in the selected Python environment."
}

$failed = @()

foreach ($package in $packages) {
    $packagePath = Join-Path $repoRoot $package.Dir
    if (-not (Test-Path $packagePath)) {
        throw "Package path not found: $packagePath"
    }

    Write-Host "==> pylint $($package.LintPath) ($($package.Dir))"
    Push-Location $packagePath
    try {
        & $python -m pylint $package.LintPath
        if ($LASTEXITCODE -ne 0) {
            $failed += $package.Dir
        }
    }
    finally {
        Pop-Location
    }
}

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "pylint failed for:"
    $failed | ForEach-Object { Write-Host " - $_" }
    exit 1
}

Write-Host ""
Write-Host "All package pylint checks passed."
