param(
  [string]$VcpkgRoot = "",
  [switch]$SetVcpkgEnv = $false,
  [ValidateSet("3.9","3.10","3.11")]
  [string]$PyVersion = "3.9"
)

$ErrorActionPreference = "Stop"

Write-Host "Setting up development environment for mini-arcade"

function Get-PythonCandidates {
  $candidates = @()

  $pyCmd = Get-Command py -ErrorAction SilentlyContinue
  if ($pyCmd) {
    $out = & py -0p 2>$null
    foreach ($line in ($out | Where-Object { $_ })) {
      # Accept: -3.11-64, -3.10, -V:3.9-64, -V:3.9
      if ($line -match '^\s*-(?:V:)?(?<tag>3\.(?:9|10|11))(?:-[^\s]+)?\s+(?<path>.+python\.exe)\s*$') {
        $candidates += [pscustomobject]@{ Tag = $Matches.tag; Path = $Matches.path.Trim() }
      }
    }
    if ($candidates.Count -gt 0) { return $candidates }
  }

  # Fallback: if no launcher, try current `python` on PATH
  $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
  if ($pythonCmd) {
    $ver = (& python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null).Trim()
    if ($ver -match '^3\.(9|10|11)$') {
      $candidates += [pscustomobject]@{ Tag = $ver; Path = $pythonCmd.Source }
      return $candidates
    } else {
      throw "Found python on PATH ($($pythonCmd.Source)) but it is $ver. Need 3.9/3.10/3.11. Install one of those or use the Python Launcher (py)."
    }
  }

  throw "No supported Python found. Install Python 3.9, 3.10, or 3.11. Recommended: install the Windows Python Launcher (py)."
}


function Select-Python {
  param(
    [string]$PreferredTag,
    [object[]]$Candidates
  )

  $allowed = @("3.9","3.10","3.11")

  $available = $Candidates | Where-Object { $allowed -contains $_.Tag }

  if (-not $available -or $available.Count -eq 0) {
    throw "No supported Python found. Install Python 3.9, 3.10, or 3.11 (and/or the Python Launcher 'py')."
  }

  # Prefer: requested -> 3.9 -> 3.10 -> 3.11
  $order = @($PreferredTag, "3.9", "3.10", "3.11") | Select-Object -Unique
  foreach ($t in $order) {
    $hit = $available | Where-Object { $_.Tag -eq $t } | Select-Object -First 1
    if ($hit) { return $hit }
  }

  # Fallback (shouldn't happen)
  return ($available | Select-Object -First 1)
}

$cands = Get-PythonCandidates
$pySel = Select-Python -PreferredTag $PyVersion -Candidates $cands

Write-Host "Using Python $($pySel.Tag): $($pySel.Path)"

# Create venv if needed (use selected python)
if (-not (Test-Path ".\.venv")) {
  & $pySel.Path -m venv .venv
}

Write-Host "Activating virtual environment and installing packages. This may take a while..."

# Activate venv
& .\.venv\Scripts\Activate.ps1

# Optional vcpkg env
if ($SetVcpkgEnv) {
  Write-Host "Setting vcpkg environment variables..."
  if (-not $VcpkgRoot) { throw "Pass -VcpkgRoot or run without -SetVcpkgEnv" }
  $env:VCPKG_ROOT = $VcpkgRoot
  $env:CMAKE_TOOLCHAIN_FILE = Join-Path $env:VCPKG_ROOT "scripts\buildsystems\vcpkg.cmake"
}

Write-Host "Installing packages..."
python -m pip install -U pip

python -m pip install -e .\packages\mini-arcade-core
python -m pip install -e .\packages\mini-arcade-pygame-backend
python -m pip install -e .\packages\mini-arcade-native-backend
python -m pip install -e .\packages\mini-arcade

Write-Host "Installing development dependencies..."
python -m pip install -U pytest pytest-cov black isort mypy pylint pre-commit
pre-commit install

Write-Host "Installing documentation dependencies..."
python -m pip install furo myst-parser sphinx sphinx-autoapi sphinx-autobuild sphinx-copybutton sphinx-design sphinx-inline-tabs sphinxcontrib-mermaid

Write-Host "Done. Try: mini-arcade --help"
