# Git Ignore Verification Script
# This script verifies that .gitignore is working correctly

Write-Host "=== Git Ignore Verification Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a git repository
if (-not (Test-Path .git)) {
    Write-Host "Error: Not in a git repository!" -ForegroundColor Red
    exit 1
}

Write-Host "Checking .gitignore configuration..." -ForegroundColor Cyan
Write-Host ""

# Test files that should be ignored
$testFiles = @(
    ".env",
    "backend/.env",
    "frontend/.env",
    "firebase-credentials.json",
    ".kiro/test-file.txt",
    ".kiro/specs/test-spec.md"
)

$allGood = $true

foreach ($file in $testFiles) {
    $result = git check-ignore -v $file 2>$null
    if ($result) {
        Write-Host "[OK] $file is ignored" -ForegroundColor Green
        Write-Host "    Rule: $result" -ForegroundColor Gray
    } else {
        Write-Host "[FAIL] $file is NOT ignored!" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""
Write-Host "Checking for tracked files that should be ignored..." -ForegroundColor Cyan
Write-Host ""

# Check for .env files in git
$trackedEnv = git ls-files | Where-Object { $_ -match '\.env$' -and $_ -notmatch '\.env\.example$' }
if ($trackedEnv) {
    Write-Host "[FAIL] Found .env files being tracked:" -ForegroundColor Red
    $trackedEnv | ForEach-Object { Write-Host "    - $_" -ForegroundColor Yellow }
    $allGood = $false
} else {
    Write-Host "[OK] No .env files are being tracked" -ForegroundColor Green
}

# Check for credential files in git
$trackedCreds = git ls-files | Where-Object { $_ -match 'credentials\.json$' -and $_ -notmatch 'example' }
if ($trackedCreds) {
    Write-Host "[FAIL] Found credential files being tracked:" -ForegroundColor Red
    $trackedCreds | ForEach-Object { Write-Host "    - $_" -ForegroundColor Yellow }
    $allGood = $false
} else {
    Write-Host "[OK] No credential files are being tracked" -ForegroundColor Green
}

# Check for .kiro files in git
$trackedKiro = git ls-files .kiro/ 2>$null
if ($trackedKiro) {
    Write-Host "[WARN] Found .kiro files being tracked:" -ForegroundColor Yellow
    $trackedKiro | ForEach-Object { Write-Host "    - $_" -ForegroundColor Gray }
    Write-Host "    Note: These were committed before .gitignore was updated." -ForegroundColor Gray
    Write-Host "    Run cleanup-git-cache.ps1 to remove them from tracking." -ForegroundColor Cyan
} else {
    Write-Host "[OK] No .kiro files are being tracked" -ForegroundColor Green
}

Write-Host ""
Write-Host "Checking for sensitive files in working directory..." -ForegroundColor Cyan
Write-Host ""

# Check if sensitive files exist locally
$sensitiveFiles = @(
    ".env",
    "backend/.env",
    "frontend/.env",
    "firebase-credentials.json"
)

foreach ($file in $sensitiveFiles) {
    if (Test-Path $file) {
        $status = git status --porcelain $file 2>$null
        if ($status) {
            Write-Host "[FAIL] $file exists and shows in git status!" -ForegroundColor Red
            $allGood = $false
        } else {
            Write-Host "[OK] $file exists but is properly ignored" -ForegroundColor Green
        }
    }
}

Write-Host ""
if ($allGood) {
    Write-Host "=== All checks passed! ===" -ForegroundColor Green
    Write-Host "Your .gitignore is working correctly." -ForegroundColor Green
} else {
    Write-Host "=== Some issues found ===" -ForegroundColor Yellow
    Write-Host "Please review the errors above." -ForegroundColor Yellow
}
Write-Host ""
