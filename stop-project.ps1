param(
    [int[]]$Ports = @(8000, 5173)
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Stop-ProcessByPort {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port
    )

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $connections) {
        Write-Host "[port:$Port] No listening process found."
        return
    }

    $processIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($processId in $processIds) {
        if ($processId -le 0) {
            continue
        }

        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if (-not $process) {
            Write-Host "[port:$Port] Process $processId already exited."
            continue
        }

        Stop-Process -Id $processId -Force
        Write-Host "[port:$Port] Stopped $($process.ProcessName) (PID: $processId)."
    }
}

foreach ($port in $Ports) {
    Stop-ProcessByPort -Port $port
}
