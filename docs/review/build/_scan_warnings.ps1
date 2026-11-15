$files = Get-ChildItem docs/review/logs/compile_*.txt
$found = $false
foreach ($f in $files) {
    $c = Get-Content $f.FullName -Raw
    $lines = ($c | Select-String -Pattern "warning" -AllMatches)
    if ($lines) {
        $found = $true
        Write-Host "=== $($f.Name) ==="
        $lines | ForEach-Object { Write-Host $_.Line }
    }
}
if (-not $found) { Write-Host "NO -Wall warnings in any compile log." }