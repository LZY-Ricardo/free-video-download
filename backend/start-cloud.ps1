Param(
  [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

Write-Host "[1/5] Check Python 3.11..."
try {
  & py -3.11 -c "import sys; print(sys.version)"
}
catch {
  Write-Error "Python 3.11 not found. Install Python 3.11 first."
  exit 1
}

$venvPython = Join-Path $PSScriptRoot ".venv/Scripts/python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
  Write-Host "[2/5] Create virtual env (.venv) with Python 3.11..."
  & py -3.11 -m venv ".venv"
}
else {
  Write-Host "[2/5] Reuse existing virtual env."
}

Write-Host "[3/5] Upgrade pip..."
& $venvPython -m pip install --upgrade pip

if (-not $SkipInstall) {
  Write-Host "[4/5] Install requirements..."
  & $venvPython -m pip install -r "requirements.txt"
}
else {
  Write-Host "[4/5] Skip dependency install (-SkipInstall)."
}

if (-not (Test-Path -LiteralPath ".env")) {
  Write-Error ".env not found in backend folder."
  exit 1
}

$envContent = Get-Content -LiteralPath ".env" -Raw
if ($envContent -notmatch 'DATABASE_URL=postgresql(\+psycopg)?://') {
  Write-Warning "DATABASE_URL is not PostgreSQL. Cloud DB mode may not be active."
}

Write-Host "[5/5] Start backend server (cloud mode)..."
Write-Host "URL: http://127.0.0.1:8000"
& $venvPython -m uvicorn app.main:app --host 0.0.0.0 --port 8000
