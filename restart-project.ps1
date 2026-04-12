param(
    [switch]$ForceInstall,
    [switch]$NoBackend,
    [switch]$NoFrontend
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$stopScript = Join-Path $root "stop-project.ps1"
$startScript = Join-Path $root "quick-start.ps1"

if (-not (Test-Path $stopScript)) {
    throw "stop-project.ps1 not found."
}

if (-not (Test-Path $startScript)) {
    throw "quick-start.ps1 not found."
}

Write-Host "[restart] Stopping existing services..."
& $stopScript

Write-Host "[restart] Starting services..."
if ($ForceInstall) {
    & $startScript -ForceInstall:$true -NoBackend:$NoBackend -NoFrontend:$NoFrontend
}
else {
    & $startScript -SkipInstall:$true -NoBackend:$NoBackend -NoFrontend:$NoFrontend
}
