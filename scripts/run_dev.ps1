# scripts/run_dev.ps1 — Anvil-compatible dev runner (Windows)
# Usage: powershell -ExecutionPolicy Bypass -File scripts\run_dev.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..
Remove-Item receipts.mock.jsonl -ErrorAction SilentlyContinue
Remove-Item C:\hummbl-broadcast-mock -Recurse -Force -ErrorAction SilentlyContinue

$job = Start-Job -ScriptBlock {
    Set-Location C:\Users\Owner\PROJECTS\hummbl-broadcast
    & .venv\Scripts\python.exe -m hummbl_broadcast.daemon --config examples\config.mock.toml
}
Start-Sleep -Seconds 4
Stop-Job $job -ErrorAction SilentlyContinue
Wait-Job $job -ErrorAction SilentlyContinue | Out-Null
Remove-Job $job -Force -ErrorAction SilentlyContinue

Write-Host "---RECEIPTS---"
if (Test-Path receipts.mock.jsonl) {
    Get-Content receipts.mock.jsonl | ForEach-Object {
        $obj = $_ | ConvertFrom-Json
        Write-Host ("  {0,-12} prompt={1} task={2}" -f $obj.event, $obj.prompt_id, $obj.task_id)
    }
} else {
    Write-Host "  (no receipts)"
}
Write-Host "---FILES---"
$files = Get-ChildItem C:\hummbl-broadcast-mock -ErrorAction SilentlyContinue
Write-Host "  $($files.Count) files in C:\hummbl-broadcast-mock"
