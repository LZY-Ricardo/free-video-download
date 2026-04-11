param(
    [switch]$SkipInstall,
    [switch]$InstallOnly,
    [switch]$NoBackend,
    [switch]$NoFrontend,
    [switch]$ForceInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"
$venvDir = Join-Path $backendDir ".venv"
$pythonExe = Join-Path $venvDir "Scripts/python.exe"
$shellExe = (Get-Process -Id $PID).Path
$npmCmd = $null

function Assert-Command {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Missing command: $Name. Please install it first."
    }
}

function Ensure-BackendDependencies {
    Assert-Command -Name "py"

    if (-not (Test-Path $venvDir)) {
        Write-Host "[backend] Creating virtual environment..."
        & py -3 -m venv "$venvDir"
    }

    if (-not (Test-Path $pythonExe)) {
        throw "Backend virtual environment exists, but Python is missing: $pythonExe"
    }

    $backendStamp = Join-Path $venvDir ".deps-ready"
    $requirementsFile = Join-Path $backendDir "requirements.txt"
    $needInstall = $ForceInstall -or -not (Test-Path $backendStamp)

    if (-not $needInstall) {
        $needInstall = (Get-Item $requirementsFile).LastWriteTime -gt (Get-Item $backendStamp).LastWriteTime
    }

    if ($needInstall) {
        Write-Host "[backend] Installing dependencies..."
        & "$pythonExe" -m pip install -r $requirementsFile
        Set-Content -Path $backendStamp -Value "ok" -NoNewline
    }
    else {
        Write-Host "[backend] Dependencies already present, skipping install."
    }
}

function Ensure-FrontendDependencies {
    if (-not $npmCmd) {
        throw "npm executable was not resolved."
    }

    $frontendStamp = Join-Path $frontendDir "node_modules/.deps-ready"
    $lockFile = Join-Path $frontendDir "package-lock.json"
    $packageFile = Join-Path $frontendDir "package.json"
    $needInstall = $ForceInstall -or -not (Test-Path (Join-Path $frontendDir "node_modules")) -or -not (Test-Path $frontendStamp)

    if (-not $needInstall) {
        $stampTime = (Get-Item $frontendStamp).LastWriteTime
        $needInstall = (Get-Item $packageFile).LastWriteTime -gt $stampTime

        if (-not $needInstall -and (Test-Path $lockFile)) {
            $needInstall = (Get-Item $lockFile).LastWriteTime -gt $stampTime
        }
    }

    if ($needInstall) {
        Write-Host "[frontend] Installing dependencies..."
        & "$npmCmd" install
        if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
            throw "Frontend install did not produce node_modules."
        }
        Set-Content -Path $frontendStamp -Value "ok" -NoNewline
    }
    else {
        Write-Host "[frontend] Dependencies already present, skipping install."
    }
}

function Start-ServiceWindow {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory,
        [Parameter(Mandatory = $true)]
        [string]$Command
    )

    Start-Process -FilePath $shellExe `
        -WorkingDirectory $WorkingDirectory `
        -ArgumentList @("-NoExit", "-Command", $Command) `
        | Out-Null
}

Push-Location $root
try {
    if (-not $NoFrontend) {
        Assert-Command -Name "node"
        $npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
        if (-not $npmCommand) {
            throw "Missing command: npm.cmd. Please install Node.js first."
        }
        $script:npmCmd = $npmCommand.Source
    }

    if (-not $SkipInstall) {
        if (-not $NoBackend) {
            Push-Location $backendDir
            try {
                Ensure-BackendDependencies
            }
            finally {
                Pop-Location
            }
        }

        if (-not $NoFrontend) {
            Push-Location $frontendDir
            try {
                Ensure-FrontendDependencies
            }
            finally {
                Pop-Location
            }
        }
    }

    if ($InstallOnly) {
        Write-Host ""
        Write-Host "Dependencies are ready."
        exit 0
    }

    if (-not $NoBackend) {
        if (-not (Test-Path $pythonExe)) {
            throw "Backend Python executable not found: $pythonExe"
        }

        Write-Host "[backend] Starting service window..."
        Start-ServiceWindow `
            -WorkingDirectory $backendDir `
            -Command "& '$pythonExe' -m app.main"
    }

    if (-not $NoFrontend) {
        Write-Host "[frontend] Starting service window..."
        Start-ServiceWindow `
            -WorkingDirectory $frontendDir `
            -Command "& '$npmCmd' run dev"
    }

    Write-Host ""
    Write-Host "Quick start completed."
    if (-not $NoFrontend) {
        Write-Host "Frontend: http://localhost:5173"
    }
    if (-not $NoBackend) {
        Write-Host "Backend: http://localhost:8000"
        Write-Host "API docs: http://localhost:8000/docs"
    }
}
finally {
    Pop-Location
}
