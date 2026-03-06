param(
  [string]$VcpkgRoot = "",
  [switch]$SetVcpkgEnv = $false,
  [switch]$PackagesOnly = $false,
  [switch]$NoCache = $false
)

$ErrorActionPreference = "Stop"

function Invoke-Pip {
  param(
    [string[]]$PipArgs
  )
  python -m pip @PipArgs
  if ($LASTEXITCODE -ne 0) {
    throw "pip command failed: python -m pip $($PipArgs -join ' ')"
  }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
  throw "Virtual environment not found at .\.venv. Run scripts/dev_install.ps1 first."
}

Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

if ($SetVcpkgEnv) {
  Write-Host "Setting vcpkg environment variables..."
  if (-not $VcpkgRoot) { throw "Pass -VcpkgRoot or run without -SetVcpkgEnv" }
  $env:VCPKG_ROOT = $VcpkgRoot
  $env:CMAKE_TOOLCHAIN_FILE = Join-Path $env:VCPKG_ROOT "scripts\buildsystems\vcpkg.cmake"
}

Write-Host "Using Python:"
python --version

$pipBase = @()
if ($NoCache) {
  $pipBase += "--no-cache-dir"
}

Write-Host "Upgrading pip tooling..."
Invoke-Pip -PipArgs ($pipBase + @("install", "-U", "pip", "setuptools", "wheel"))

$distPkgs = @(
  "mini-arcade",
  "mini-arcade-native-backend",
  "mini-arcade-pygame-backend",
  "mini-arcade-core"
)

Write-Host "Uninstalling local mini-arcade packages..."
Invoke-Pip -PipArgs (@("uninstall", "-y") + $distPkgs)

$editablePkgs = @(
  ".\packages\mini-arcade-core",
  ".\packages\mini-arcade-pygame-backend",
  ".\packages\mini-arcade-native-backend",
  ".\packages\mini-arcade"
)

foreach ($pkg in $editablePkgs) {
  Write-Host "Installing editable package $pkg ..."
  $installArgs = $pipBase + @("install", "-e", $pkg)
  if ($pkg -eq ".\packages\mini-arcade") {
    # Keep top-level package editable without letting pip replace local backends from index.
    $installArgs += "--no-deps"
  }
  Invoke-Pip -PipArgs $installArgs
}

if (-not $PackagesOnly) {
  Write-Host "Reinstalling dev dependencies..."
  Invoke-Pip -PipArgs (
    $pipBase + @(
      "install",
      "--force-reinstall",
      "-U",
      "pytest",
      "pytest-cov",
      "black",
      "isort",
      "mypy",
      "pylint",
      "pre-commit"
    )
  )

  Write-Host "Installing pre-commit hooks..."
  pre-commit install

  Write-Host "Reinstalling documentation dependencies..."
  Invoke-Pip -PipArgs (
    $pipBase + @(
      "install",
      "furo",
      "myst-parser",
      "sphinx",
      "sphinx-autoapi",
      "sphinx-autobuild",
      "sphinx-copybutton",
      "sphinx-design",
      "sphinx-inline-tabs",
      "sphinxcontrib-mermaid"
    )
  )
}

Write-Host "Done. Mini Arcade dependencies were reinstalled."
