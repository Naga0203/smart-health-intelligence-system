# Git Cache Cleanup Script
# This script removes files from git tracking that should be ignored

Write-Host "=== Git Cache Cleanup Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a git repository
if (-not (Test-Path .git)) {
    Write-Host "Error: Not in a git repository!" -ForegroundColor Red
    exit 1
}

Write-Host "This script will remove the following from git tracking:" -ForegroundColor Yellow
Write-Host "  - Old .kiro files that were previously committed" -ForegroundColor Yellow
Write-Host "  - Any .env files (if tracked)" -ForegroundColor Yellow
Write-Host "  - Any credential files (if tracked)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Note: Files will NOT be deleted from your disk, only from git tracking." -ForegroundColor Green
Write-Host ""

$response = Read-Host "Do you want to continue? (y/n)"
if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "Aborted." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Removing old .kiro files from git tracking..." -ForegroundColor Cyan

# Remove .kiro files from git cache (but keep them on disk)
$kiroFiles = git ls-files .kiro/
if ($kiroFiles) {
    Write-Host "Found .kiro files in git tracking:" -ForegroundColor Yellow
    $kiroFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    git rm -r --cached .kiro/
    Write-Host "Removed .kiro files from git tracking." -ForegroundColor Green
} else {
    Write-Host "No .kiro files found in git tracking." -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 2: Checking for .env files..." -ForegroundColor Cyan

# Check for any .env files (excluding .env.example)
$envFiles = git ls-files | Where-Object { $_ -match '\.env$' -and $_ -notmatch '\.env\.example$' }
if ($envFiles) {
    Write-Host "Found .env files in git tracking:" -ForegroundColor Yellow
    $envFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    $envFiles | ForEach-Object { git rm --cached $_ }
    Write-Host "Removed .env files from git tracking." -ForegroundColor Green
} else {
    Write-Host "No .env files found in git tracking." -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 3: Checking for credential files..." -ForegroundColor Cyan

# Check for credential files
$credFiles = git ls-files | Where-Object { $_ -match 'credentials' }
if ($credFiles) {
    Write-Host "Found credential files in git tracking:" -ForegroundColor Yellow
    $credFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    $credFiles | ForEach-Object { git rm --cached $_ }
    Write-Host "Removed credential files from git tracking." -ForegroundColor Green
} else {
    Write-Host "No credential files found in git tracking." -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 4: Checking git status..." -ForegroundColor Cyan
git status --short

Write-Host ""
Write-Host "=== Cleanup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Review the changes with: git status" -ForegroundColor White
Write-Host "2. Commit the changes with: git commit -m 'chore: update .gitignore and remove tracked files'" -ForegroundColor White
Write-Host "3. Push to remote with: git push" -ForegroundColor White
Write-Host ""
Write-Host "Note: Your local files are safe and have not been deleted." -ForegroundColor Green
