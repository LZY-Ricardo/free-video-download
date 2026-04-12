param(
    [int]$ExpireHours = 24
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$downloadsDir = Join-Path $PSScriptRoot "downloads"
if (-not (Test-Path $downloadsDir)) {
    Write-Host "downloads directory not found."
    exit 0
}

$cutoff = (Get-Date).AddHours(-$ExpireHours)
$removed = 0

Get-ChildItem $downloadsDir -File | ForEach-Object {
    if ($_.LastWriteTime -lt $cutoff) {
        Remove-Item -LiteralPath $_.FullName -Force
        $removed += 1
    }
}

Write-Host "Removed $removed files."
