# EXO_GANS Sovereign Edge Setup

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   EXO_GANS Sovereign Edge Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Virtual Environment
Write-Host "[1/3] Setting up Python Virtual Environment..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "   Created .venv/" -ForegroundColor Green
} else {
    Write-Host "   .venv/ already exists." -ForegroundColor Green
}

Write-Host "   Installing dependencies (this may take a minute)..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt | Out-Null
Write-Host "   Dependencies installed successfully." -ForegroundColor Green
Write-Host ""

# 2. Datacenter Check
Write-Host "[2/3] Verifying 5-Tier Datacenter..." -ForegroundColor Yellow
if (Test-Path "__DATACENTER\GLOBAL") {
    Write-Host "   Sovereign Datacenter detected and seeded with core agents." -ForegroundColor Green
} else {
    Write-Host "   Warning: __DATACENTER\GLOBAL not found in repository root." -ForegroundColor Red
}
Write-Host ""

# 3. OmniBuilder PATH Registration
Write-Host "[3/3] Omni CI/CD Configuration" -ForegroundColor Yellow
Write-Host "The OmniBuilder Daemon ensures scripts run securely in your Sovereign Edge."
$addPath = Read-Host "Would you like to automatically add the Omni tools directory to your System PATH? (Y/N)"

if ($addPath -match "^[yY]$") {
    $omniPath = Resolve-Path ".\tools\omni"
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    
    if ($currentPath -notmatch [regex]::Escape($omniPath)) {
        $newPath = $currentPath + ";" + $omniPath
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Host "   Success! '$omniPath' added to your PATH." -ForegroundColor Green
        Write-Host "   You may need to restart your terminal for 'omni' to be recognized." -ForegroundColor Yellow
    } else {
        Write-Host "   Omni is already in your PATH." -ForegroundColor Green
    }
} else {
    Write-Host "   Skipping PATH registration." -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   SETUP COMPLETE" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Authentication is handled natively via Windows DPAPI (no .env files required)." -ForegroundColor White
Write-Host "To securely vault your API keys:" -ForegroundColor White
Write-Host "  > Launch the TUI and use the 'Set API Key' modal, or..." -ForegroundColor DarkGray
Write-Host "  > Run: .\.venv\Scripts\python.exe maccre.py config set-key <YOUR_KEY>" -ForegroundColor DarkGray
Write-Host ""
Write-Host "To start the Terminal UI:" -ForegroundColor White
Write-Host "  > .\.venv\Scripts\python.exe main.py" -ForegroundColor Green
Write-Host ""
Write-Host "Welcome to the Sovereign Edge." -ForegroundColor Yellow
