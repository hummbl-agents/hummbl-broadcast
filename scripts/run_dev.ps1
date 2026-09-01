# scripts/run_dev.ps1 — Anvil-compatible dev runner (Windows)
# Usage: powershell -ExecutionPolicy Bypass -File scripts\run_dev.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSCommandPath) | Split-Path -Parent
$root = (Get-Location).Path
Write-Host "Working in: $root"

Remove-Item "$root\receipts.mock.jsonl" -ErrorAction SilentlyContinue
Remove-Item "$root\out\mock" -Recurse -Force -ErrorAction SilentlyContinue

$proc = Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "-m","hummbl_broadcast.daemon","--config","examples\config.mock.toml" -WorkingDirectory $root -PassThru -NoNewWindow
Start-Sleep -Seconds 3
Stop-Process $proc -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

Write-Host "---RECEIPTS---"
$receiptsPath = "$root\receipts.mock.jsonl"
if (Test-Path $receiptsPath) {
    $lines = Get-Content $receiptsPath
    Write-Host "  Total: $($lines.Count) lines"
    $lines | Select-Object -First 20 | ForEach-Object {
        $obj = $_ | ConvertFrom-Json
        Write-Host ("    {0,-12} prompt={1}" -f $obj.event, $obj.prompt_id)
    }
} else {
    Write-Host "  (no receipts)"
}

Write-Host "---FILES---"
$outDir = "$root\out\mock"
$files = Get-ChildItem $outDir -ErrorAction SilentlyContinue
Write-Host "  $($files.Count) files in $outDir"
