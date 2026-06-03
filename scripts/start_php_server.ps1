$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$xamppPhp = "C:\xampp\php\php.exe"

if (Test-Path $xamppPhp) {
    $php = $xamppPhp
} else {
    $phpCommand = Get-Command php -ErrorAction SilentlyContinue
    if ($null -eq $phpCommand) {
        Write-Host "PHP was not found. Install XAMPP or add PHP to PATH." -ForegroundColor Red
        exit 1
    }
    $php = $phpCommand.Source
}

Set-Location $projectRoot
Write-Host "Starting Gemma4 demo at http://127.0.0.1:8080" -ForegroundColor Green
Write-Host "Using PHP: $php" -ForegroundColor Cyan
& $php -S 127.0.0.1:8080 router.php
